import logging
from datetime import datetime, timedelta, timezone
from typing import Any

import jwt
from pwdlib import PasswordHash
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.models.database.user import User
from app.models.errors import InvalidCredentials
from app.models.schemas.user import TokenData

logger = logging.getLogger(__name__)

password_hash = PasswordHash.recommended()


async def authenticate_user(
    username: str,
    password: str,
    db: AsyncSession,
) -> User | None:
    result = await db.execute(select(User).where(User.username == username))
    user = result.scalar_one_or_none()
    if not user or not password_hash.verify(password, user.password_hash):
        return None
    return user


def create_token(username: str, expires_delta: timedelta):
    payload: dict[str, Any] = {
        "sub": username,
        "exp": datetime.now(timezone.utc) + expires_delta,
    }
    token = jwt.encode(payload, settings.JWT_SECRET_KEY, algorithm=settings.ALGORITHM)
    return str(token)


def create_access_token(username: str):
    return create_token(
        username,
        expires_delta=timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES),
    )


def create_refresh_token(username: str):
    return create_token(
        username,
        expires_delta=timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS),
    )


def verify_token(token: str) -> str:
    try:
        # checks expiration
        payload = jwt.decode(
            token, settings.JWT_SECRET_KEY, algorithms=[settings.ALGORITHM]
        )
    except Exception as e:
        logger.error(f"JWT decode error: {e}")
        raise InvalidCredentials()

    username = payload.get("sub")
    if not username:
        logger.error("JWT payload missing 'sub' field")
        raise InvalidCredentials()

    try:
        token_data = TokenData(username=username)
    except Exception as e:
        logger.error(f"TokenData validation error: {e}")
        raise InvalidCredentials()

    return token_data.username
