import logging
from dataclasses import dataclass

from fastapi import BackgroundTasks
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.database.access_request import AccessRequest, AccessRequestStatus
from app.models.database.user import User
from app.models.errors import (
    AccessRequestPending,
    AccessRequestRejected,
    EmailAlreadyRegistered,
)

from .email import EmailService

logger = logging.getLogger(__name__)


@dataclass
class AccessRequestResult:
    already_approved: bool
    access_request: AccessRequest


async def request_access(
    db: AsyncSession,
    email: str,
    first_name: str,
    last_name: str,
    email_svc: EmailService,
    background_tasks: BackgroundTasks,
) -> AccessRequestResult:
    logger.info(f"Access request received for email: {email}")

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
                return AccessRequestResult(
                    already_approved=True,
                    access_request=existing_request,
                )

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

    return AccessRequestResult(
        already_approved=False,
        access_request=access_request,
    )
