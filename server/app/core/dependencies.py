import logging
from collections.abc import AsyncGenerator

import jwt
from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from typing_extensions import Annotated

from app.core.config import settings
from app.models.database.user import User
from app.models.errors import InsufficientPermissions, InvalidCredentials
from app.models.schemas.user import TokenData, UserPublic

logger = logging.getLogger(__name__)

async_engine = create_async_engine(
    settings.DATABASE_URL,
    echo=settings.ENV != "prod",
)

AsyncSessionLocal = async_sessionmaker(
    bind=async_engine,
    expire_on_commit=False,
)


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with AsyncSessionLocal() as session:
        yield session


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="api/auth/login")


async def get_current_user(
    token: Annotated[str, Depends(oauth2_scheme)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> UserPublic:
    logger.info("Getting current user using token")

    try:
        # checks expiration
        payload = jwt.decode(
            token,
            settings.JWT_SECRET_KEY,
            algorithms=[settings.ALGORITHM],
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

    user = (
        await db.execute(select(User).where(User.username == token_data.username))
    ).scalar_one_or_none()
    if not user:
        raise InvalidCredentials()

    return UserPublic.model_validate(user, from_attributes=True)


async def get_current_admin(
    user: Annotated[UserPublic, Depends(get_current_user)],
) -> UserPublic:
    logger.info("Getting current admin user")

    if not user.is_admin:
        logger.error(f"User {user.username} is not an admin")
        raise InsufficientPermissions()
    return user
