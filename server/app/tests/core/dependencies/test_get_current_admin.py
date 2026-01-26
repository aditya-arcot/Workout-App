import pytest
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.dependencies import get_current_admin
from app.models.database.user import User
from app.models.errors import InsufficientPermissions
from app.models.schemas.user import UserPublic


async def get_admin(session: AsyncSession):
    result = await session.execute(
        select(User).where(User.username == settings.admin.username)
    )
    admin = result.scalar_one()
    adminPublic = UserPublic.model_validate(admin, from_attributes=True)
    return adminPublic


async def test_get_current_admin(session: AsyncSession):
    admin = await get_admin(session)
    admin = await get_current_admin(user=admin)

    assert admin.username == settings.admin.username
    assert admin.is_admin is True


async def test_get_current_admin_non_admin(session: AsyncSession):
    admin = await get_admin(session)
    admin.is_admin = False

    with pytest.raises(InsufficientPermissions):
        await get_current_admin(user=admin)
