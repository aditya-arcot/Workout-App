import jwt
import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.models.errors import InvalidCredentials
from app.services.auth import login


async def test_login(session: AsyncSession):
    result = await login(
        username=settings.admin.username,
        password=settings.admin.password,
        db=session,
    )

    payload = jwt.decode(
        result.access_token,
        settings.jwt.secret_key,
        algorithms=[settings.jwt.algorithm],
    )

    assert payload["sub"] == settings.admin.username
    assert "exp" in payload


async def test_login_non_existent_user(session: AsyncSession):
    with pytest.raises(InvalidCredentials):
        await login(
            username="non_existent_user",
            password="some_password",
            db=session,
        )


async def test_login_invalid_password(session: AsyncSession):
    with pytest.raises(InvalidCredentials):
        await login(
            username=settings.admin.username,
            password="some_password",
            db=session,
        )
