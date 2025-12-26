from fastapi import status
from httpx import AsyncClient

from app.tests.api.utilities import HttpMethod, login_admin, make_http_request


async def get_current_user(client: AsyncClient):
    return await make_http_request(
        client, method=HttpMethod.GET, endpoint="/api/users/current"
    )


async def logout(client: AsyncClient):
    return await make_http_request(
        client, method=HttpMethod.POST, endpoint="/api/auth/logout"
    )


async def test_logout(client: AsyncClient):
    await login_admin(client)

    resp = await get_current_user(client)
    assert resp.status_code == status.HTTP_200_OK

    resp = await logout(client)
    assert resp.status_code == status.HTTP_204_NO_CONTENT

    resp = await get_current_user(client)
    assert resp.status_code == status.HTTP_401_UNAUTHORIZED


async def test_logout_not_logged_in(client: AsyncClient):
    resp = await logout(client)
    assert resp.status_code == status.HTTP_204_NO_CONTENT

    resp = await get_current_user(client)
    assert resp.status_code == status.HTTP_401_UNAUTHORIZED
