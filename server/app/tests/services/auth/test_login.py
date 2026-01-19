import jwt
import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.models.errors import InvalidCredentials
from app.services.auth import login


async def test_login(session: AsyncSession):
    result = await login(
        username=settings.ADMIN_USERNAME,
        password=settings.ADMIN_PASSWORD,
        db=session,
    )

    payload = jwt.decode(
        result.access_token,
        settings.JWT_SECRET_KEY,
        algorithms=[settings.ALGORITHM],
    )

    assert payload["sub"] == settings.ADMIN_USERNAME
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
            username=settings.ADMIN_USERNAME,
            password="some_password",
            db=session,
        )
