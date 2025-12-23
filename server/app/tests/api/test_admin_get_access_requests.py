from httpx import AsyncClient
from sqlalchemy import update
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.models.database.user import User
from app.models.schemas.user import UserPublic
from app.tests.api.utilities import HttpMethod, login_and_get_token, make_http_request


async def make_request(client: AsyncClient, token: str | None = None):
    return await make_http_request(
        client,
        method=HttpMethod.GET,
        endpoint="/api/admin/access-requests",
        token=token,
    )


async def test_get_access_requests(client: AsyncClient):
    token = await login_and_get_token(client)
    resp = await make_request(client, token=token)

    assert resp.status_code == 200
    body = resp.json()
    assert isinstance(body, list)
    for item in body:  # type: ignore
        UserPublic.model_validate(item)


async def test_get_access_requests_no_token(client: AsyncClient):
    resp = await make_request(client)

    assert resp.status_code == 401
    body = resp.json()
    assert body["detail"] == "Not authenticated"


async def test_get_access_requests_non_admin_user(
    client: AsyncClient, session: AsyncSession
):
    await session.execute(
        update(User)
        .where(User.username == settings.ADMIN_USERNAME)
        .values(is_admin=False)
    )
    await session.commit()

    token = await login_and_get_token(client)
    resp = await make_request(client, token=token)

    assert resp.status_code == 403
    body = resp.json()
    assert body["detail"] == "Insufficient permissions"
