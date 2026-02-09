import logging
import secrets
from datetime import datetime, timezone
from typing import Tuple

from fastapi import BackgroundTasks
from sqlalchemy import func, select, update
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.config import settings
from app.core.security import (
    authenticate_user,
    create_access_token,
    create_refresh_token,
    password_hash,
    verify_token,
)
from app.models.api import LoginResult
from app.models.database.access_request import AccessRequest, AccessRequestStatus
from app.models.database.password_reset_token import PasswordResetToken
from app.models.database.registration_token import RegistrationToken
from app.models.database.user import User
from app.models.errors import (
    AccessRequestPending,
    AccessRequestRejected,
    EmailAlreadyRegistered,
    InvalidCredentials,
    InvalidToken,
    UsernameAlreadyRegistered,
)

from .email import EmailService

logger = logging.getLogger(__name__)


async def get_registration_token(
    token_str: str,
    db: AsyncSession,
) -> RegistrationToken | None:
    # Extract prefix from token for efficient lookup
    token_prefix = token_str[:12]
    
    # First try: lookup by token_prefix (O(1) operation)
    tokens = (
        (
            await db.execute(
                select(RegistrationToken)
                .options(selectinload(RegistrationToken.access_request))
                .where(RegistrationToken.used_at.is_(None))
                .where(RegistrationToken.expires_at > func.now())
                .where(RegistrationToken.token_prefix == token_prefix)
                .order_by(RegistrationToken.created_at.desc())
            )
        )
        .scalars()
        .all()
    )
    for token in tokens:
        if password_hash.verify(token_str, token.token_hash):
            return token
    
    # Fallback: check tokens with null prefix (legacy tokens, O(n) operation)
    # This handles backward compatibility for tokens created before the optimization
    legacy_tokens = (
        (
            await db.execute(
                select(RegistrationToken)
                .options(selectinload(RegistrationToken.access_request))
                .where(RegistrationToken.used_at.is_(None))
                .where(RegistrationToken.expires_at > func.now())
                .where(RegistrationToken.token_prefix.is_(None))
                .order_by(RegistrationToken.created_at.desc())
            )
        )
        .scalars()
        .all()
    )
    for token in legacy_tokens:
        if password_hash.verify(token_str, token.token_hash):
            return token


async def expire_existing_registration_tokens(
    access_request_id: int,
    db: AsyncSession,
) -> None:
    logger.info(
        f"Expiring existing registration tokens for access request {access_request_id}"
    )

    now = datetime.now(timezone.utc)
    await db.execute(
        update(RegistrationToken)
        .where(
            RegistrationToken.access_request_id == access_request_id,
            RegistrationToken.expires_at > now,
        )
        .values(expires_at=now)
    )


def create_registration_token(
    access_request_id: int,
) -> Tuple[str, RegistrationToken]:
    logger.info(
        f"Creating new registration token for access request {access_request_id}"
    )

    token_str = secrets.token_urlsafe(32)
    token_hash = password_hash.hash(token_str)
    token_prefix = token_str[:12]  # Store first 12 chars as lookup key

    token = RegistrationToken(
        access_request_id=access_request_id,
        token_hash=token_hash,
        token_prefix=token_prefix,
    )
    return token_str, token


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
        logger.info(
            f"Found existing access request for email {email} with id {existing_request.id}"
        )
        match existing_request.status:
            case AccessRequestStatus.PENDING:
                raise AccessRequestPending()
            case AccessRequestStatus.REJECTED:
                raise AccessRequestRejected()
            case AccessRequestStatus.APPROVED:
                await expire_existing_registration_tokens(existing_request.id, db)

                token_str, token = create_registration_token(existing_request.id)
                db.add(token)
                await db.commit()

                if settings.env == "test":
                    await db.refresh(existing_request)
                    await db.refresh(token)

                background_tasks.add_task(
                    email_svc.send_access_request_approved_email,
                    existing_request,
                    token_str,
                )
                return True

    logger.info(f"Creating new access request for email: {email}")
    access_request = AccessRequest(
        email=email,
        first_name=first_name,
        last_name=last_name,
    )
    db.add(access_request)
    await db.commit()

    if settings.env == "test":
        await db.refresh(access_request)

    admins = (await db.execute(select(User).where(User.is_admin))).scalars().all()
    for admin in admins:
        background_tasks.add_task(
            email_svc.send_access_request_notification, admin.email, access_request
        )

    return False


async def register(
    token_str: str,
    username: str,
    password: str,
    db: AsyncSession,
) -> None:
    logger.info(f"Registering new user {username}")

    token = await get_registration_token(token_str, db)
    if not token or token.is_used() or token.is_expired():
        raise InvalidToken()

    access_request = token.access_request
    if access_request.status != AccessRequestStatus.APPROVED:
        raise InvalidToken()

    existing_user = (
        await db.execute(select(User).where(User.username == username))
    ).scalar_one_or_none()
    if existing_user:
        raise UsernameAlreadyRegistered()

    token.used_at = datetime.now(timezone.utc)
    await expire_existing_registration_tokens(access_request.id, db)

    user = User(
        username=username,
        email=access_request.email,
        first_name=access_request.first_name,
        last_name=access_request.last_name,
        password_hash=password_hash.hash(password),
    )
    db.add(user)
    await db.commit()


async def get_password_reset_token(
    token_str: str,
    db: AsyncSession,
) -> PasswordResetToken | None:
    # Extract prefix from token for efficient lookup
    token_prefix = token_str[:12]
    
    # First try: lookup by token_prefix (O(1) operation)
    tokens = (
        (
            await db.execute(
                select(PasswordResetToken)
                .options(selectinload(PasswordResetToken.user))
                .where(PasswordResetToken.used_at.is_(None))
                .where(PasswordResetToken.expires_at > func.now())
                .where(PasswordResetToken.token_prefix == token_prefix)
                .order_by(PasswordResetToken.created_at.desc())
            )
        )
        .scalars()
        .all()
    )
    for token in tokens:
        if password_hash.verify(token_str, token.token_hash):
            return token
    
    # Fallback: check tokens with null prefix (legacy tokens, O(n) operation)
    # This handles backward compatibility for tokens created before the optimization
    legacy_tokens = (
        (
            await db.execute(
                select(PasswordResetToken)
                .options(selectinload(PasswordResetToken.user))
                .where(PasswordResetToken.used_at.is_(None))
                .where(PasswordResetToken.expires_at > func.now())
                .where(PasswordResetToken.token_prefix.is_(None))
                .order_by(PasswordResetToken.created_at.desc())
            )
        )
        .scalars()
        .all()
    )
    for token in legacy_tokens:
        if password_hash.verify(token_str, token.token_hash):
            return token


async def expire_existing_password_reset_tokens(
    user_id: int,
    db: AsyncSession,
) -> None:
    logger.info(f"Expiring existing password reset tokens for user {user_id}")

    now = datetime.now(timezone.utc)
    await db.execute(
        update(PasswordResetToken)
        .where(
            PasswordResetToken.user_id == user_id,
            PasswordResetToken.expires_at > now,
        )
        .values(expires_at=now)
    )


def create_password_reset_token(
    user_id: int,
) -> Tuple[str, PasswordResetToken]:
    logger.info(f"Creating new password reset token for user {user_id}")

    token_str = secrets.token_urlsafe(32)
    token_hash = password_hash.hash(token_str)
    token_prefix = token_str[:12]  # Store first 12 chars as lookup key

    token = PasswordResetToken(
        user_id=user_id,
        token_hash=token_hash,
        token_prefix=token_prefix,
    )
    return token_str, token


async def request_password_reset(
    email: str,
    background_tasks: BackgroundTasks,
    db: AsyncSession,
    email_svc: EmailService,
) -> None:
    logger.info(f"Requesting password reset for email: {email}")

    user = (
        await db.execute(select(User).where(User.email == email))
    ).scalar_one_or_none()
    if not user:
        logger.info(f"Password reset requested for unregistered email: {email}")
        return

    await expire_existing_password_reset_tokens(user.id, db)

    token_str, token = create_password_reset_token(user.id)
    db.add(token)
    await db.commit()

    if settings.env == "test":
        await db.refresh(user)
        await db.refresh(token)

    background_tasks.add_task(
        email_svc.send_password_reset_email,
        user.email,
        token_str,
    )


async def reset_password(
    token_str: str,
    password: str,
    db: AsyncSession,
) -> None:
    logger.info("Resetting password")

    token = await get_password_reset_token(token_str, db)
    if not token or token.is_used() or token.is_expired():
        raise InvalidToken()

    user = token.user
    token.used_at = datetime.now(timezone.utc)
    await expire_existing_password_reset_tokens(user.id, db)

    user.password_hash = password_hash.hash(password)
    await db.commit()


async def login(username: str, password: str, db: AsyncSession) -> LoginResult:
    logger.info(f"Logging in user {username}")

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
