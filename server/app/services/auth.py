import logging

from fastapi import BackgroundTasks
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import (
    authenticate_user,
    create_access_token,
    create_refresh_token,
    verify_token,
)
from app.models.api import LoginResult
from app.models.database.access_request import AccessRequest, AccessRequestStatus
from app.models.database.user import User
from app.models.errors import (
    AccessRequestPending,
    AccessRequestRejected,
    EmailAlreadyRegistered,
    InvalidCredentials,
)

from .email import EmailService

logger = logging.getLogger(__name__)


async def request_access(
    email: str,
    first_name: str,
    last_name: str,
    background_tasks: BackgroundTasks,
    db: AsyncSession,
    email_svc: EmailService,
) -> bool:
    """Returns True if access was already approved, False otherwise"""
    logger.info(f"Requesting access for email: {email}")

    existing_user = (
        await db.execute(select(User).where(User.email == email))
    ).scalar_one_or_none()
    if existing_user:
        raise EmailAlreadyRegistered()

    existing_request = (
        await db.execute(
            select(AccessRequest)
            .where(AccessRequest.email == email)
            .order_by(AccessRequest.created_at.desc())
            .limit(1)
        )
    ).scalar_one_or_none()
    if existing_request:
        match existing_request.status:
            case AccessRequestStatus.PENDING:
                raise AccessRequestPending()
            case AccessRequestStatus.REJECTED:
                raise AccessRequestRejected()
            case AccessRequestStatus.APPROVED:
                background_tasks.add_task(
                    email_svc.send_access_request_approved_email, existing_request
                )
                return True

    access_request = AccessRequest(
        email=email,
        first_name=first_name,
        last_name=last_name,
    )

    db.add(access_request)
    await db.commit()
    await db.refresh(access_request)

    admins = (await db.execute(select(User).where(User.is_admin))).scalars().all()
    for admin in admins:
        background_tasks.add_task(
            email_svc.send_access_request_notification, admin.email, access_request
        )

    return False


async def login(username: str, password: str, db: AsyncSession) -> LoginResult:
    logger.info(f"Logging in for user: {username}")

    user = await authenticate_user(username, password, db)
    if not user:
        raise InvalidCredentials()

    access_token = create_access_token(user.username)
    refresh_token = create_refresh_token(user.username)

    return LoginResult(
        access_token=access_token,
        refresh_token=refresh_token,
    )


async def refresh(db: AsyncSession, token: str) -> str:
    logger.info("Refreshing access token")

    username = verify_token(token)
    user = (
        await db.execute(select(User).where(User.username == username))
    ).scalar_one_or_none()
    if not user:
        raise InvalidCredentials()

    return create_access_token(user.username)
