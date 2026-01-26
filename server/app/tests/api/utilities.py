from enum import Enum
from typing import Any

from httpx import AsyncClient

from app.core.config import settings


class HttpMethod(str, Enum):
    GET = "get"
    POST = "post"
    DELETE = "delete"
    PUT = "put"
    PATCH = "patch"


async def make_http_request(
    client: AsyncClient,
    *,
    method: HttpMethod,
    endpoint: str,
    headers: dict[str, str] | None = None,
    json: dict[str, Any] | None = None,
):
    if headers is None:
        headers = {}

    if method == HttpMethod.GET:
        return await client.get(endpoint, headers=headers)
    elif method == HttpMethod.POST:
        return await client.post(endpoint, json=json, headers=headers)
    elif method == HttpMethod.DELETE:
        return await client.delete(endpoint, headers=headers)
    elif method == HttpMethod.PUT:
        return await client.put(endpoint, json=json, headers=headers)
    else:  # patch
        return await client.patch(endpoint, json=json, headers=headers)


async def login_admin(
    client: AsyncClient,
):
    return await login(
        client,
        username=settings.admin.username,
        password=settings.admin.password,
    )


async def login(
    client: AsyncClient,
    *,
    username: str,
    password: str,
):
    return await make_http_request(
        client,
        method=HttpMethod.POST,
        endpoint="/api/auth/login",
        json={
            "username": username,
            "password": password,
        },
    )
