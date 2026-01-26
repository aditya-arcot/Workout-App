from fastapi import status
from httpx import AsyncClient

from app.core.config import settings
from app.models.errors import InvalidCredentials
from app.tests.api.utilities import login, login_admin


async def test_login(client: AsyncClient):
    resp = await login_admin(client)

    assert resp.status_code == status.HTTP_204_NO_CONTENT
    assert "access_token" in resp.cookies


async def test_login_non_existent_user(client: AsyncClient):
    resp = await login(client, username="non_existent_user", password="some_password")

    assert resp.status_code == InvalidCredentials.status_code
    body = resp.json()
    assert body["detail"] == InvalidCredentials.detail


async def test_login_invalid_password(client: AsyncClient):
    resp = await login(
        client, username=settings.admin.username, password="some_password"
    )

    assert resp.status_code == InvalidCredentials.status_code
    body = resp.json()
    assert body["detail"] == InvalidCredentials.detail
