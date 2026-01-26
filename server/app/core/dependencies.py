import logging
from collections.abc import AsyncGenerator

from fastapi import Depends
from fastapi.security import APIKeyCookie
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from typing_extensions import Annotated

from app.core.config import settings
from app.core.security import verify_token
from app.models.database.user import User
from app.models.errors import InsufficientPermissions, InvalidCredentials
from app.models.schemas.user import UserPublic

logger = logging.getLogger(__name__)

async_engine = create_async_engine(
    settings.database.url,
    echo=not settings.is_prod,
)

AsyncSessionLocal = async_sessionmaker(
    bind=async_engine,
    expire_on_commit=False,
)


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with AsyncSessionLocal() as session:
        yield session


access_token_cookie = APIKeyCookie(
    name="access_token",
)

refresh_token_cookie = APIKeyCookie(
    name="refresh_token",
)


async def get_current_user(
    token: Annotated[str, Depends(access_token_cookie)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> UserPublic:
    logger.info("Getting current user using token")

    username = verify_token(token)
    user = (
        await db.execute(select(User).where(User.username == username))
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
