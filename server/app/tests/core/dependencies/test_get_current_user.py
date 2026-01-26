import time
from typing import Any

import jwt
import pytest
from sqlalchemy import delete
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.dependencies import get_current_user
from app.models.database.user import User
from app.models.errors import InvalidCredentials


def make_token(payload: dict[str, Any], secret: str = settings.jwt.secret_key) -> str:
    token = jwt.encode(payload, secret, algorithm=settings.jwt.algorithm)
    return str(token)


async def test_get_current_user(session: AsyncSession):
    token = make_token({"sub": settings.admin.username})
    user = await get_current_user(token=token, db=session)

    assert user.username == settings.admin.username
    assert user.email == settings.admin.email
    assert user.first_name == settings.admin.first_name
    assert user.last_name == settings.admin.last_name
    assert user.is_admin is True


async def test_get_current_user_missing_sub(session: AsyncSession):
    token = make_token({})

    with pytest.raises(InvalidCredentials):
        await get_current_user(token=token, db=session)


async def test_get_current_user_invalid_secret(session: AsyncSession):
    token = make_token({"sub": settings.admin.username}, secret="wrong_secret")

    with pytest.raises(InvalidCredentials):
        await get_current_user(token=token, db=session)


async def test_get_current_user_expired_token(session: AsyncSession):
    past_time = int(time.time()) - 3600
    token = make_token({"sub": settings.admin.username, "exp": past_time})

    with pytest.raises(InvalidCredentials):
        await get_current_user(token=token, db=session)


async def test_get_current_user_deleted_user(session: AsyncSession):
    token = make_token({"sub": settings.admin.username})

    await session.execute(delete(User).where(User.username == settings.admin.username))
    await session.commit()

    with pytest.raises(InvalidCredentials):
        await get_current_user(token=token, db=session)
