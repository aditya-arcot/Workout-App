from httpx import AsyncClient
from sqlalchemy import update
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.models.database.user import User
from app.models.schemas.user import UserPublic
from app.tests.api.utilities import HttpMethod, login_admin, make_http_request


async def make_request(client: AsyncClient):
    return await make_http_request(
        client,
        method=HttpMethod.GET,
        endpoint="/api/admin/access-requests",
    )


async def test_get_access_requests(client: AsyncClient):
    await login_admin(client)
    resp = await make_request(client)

    assert resp.status_code == 200
    body = resp.json()
    assert isinstance(body, list)
    for item in body:
        UserPublic.model_validate(item)


async def test_get_access_requests_non_admin_user(
    client: AsyncClient, session: AsyncSession
):
    await session.execute(
        update(User)
        .where(User.username == settings.admin.username)
        .values(is_admin=False)
    )
    await session.commit()

    await login_admin(client)
    resp = await make_request(client)

    assert resp.status_code == 403
    body = resp.json()
    assert body["detail"] == "Insufficient permissions"
