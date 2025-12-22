from fastapi import status
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.database.access_request import AccessRequest, AccessRequestStatus
from app.models.database.user import User
from app.models.errors import (
    AccessRequestPending,
    AccessRequestRejected,
    EmailAlreadyRegistered,
)


async def test_request_access(client: AsyncClient):
    resp = await client.post(
        "/api/auth/request-access",
        json={
            "email": "newuser@example.com",
            "first_name": "New",
            "last_name": "User",
        },
    )

    assert resp.status_code == status.HTTP_200_OK
    body = resp.json()
    assert body["detail"] == "Access request created. Please wait for admin approval."
    assert body["access_request_id"] is not None


async def test_request_access_approved(client: AsyncClient, session: AsyncSession):
    req = AccessRequest(
        email="approved@example.com",
        first_name="Approved",
        last_name="User",
        status=AccessRequestStatus.APPROVED,
    )
    session.add(req)
    await session.commit()

    resp = await client.post(
        "/api/auth/request-access",
        json={
            "email": "approved@example.com",
            "first_name": "Test",
            "last_name": "User",
        },
    )

    assert resp.status_code == status.HTTP_200_OK
    body = resp.json()
    assert body["detail"] == "Access request already approved. Approval email resent."
    assert body["access_request_id"] is not None


async def test_request_access_existing_user(client: AsyncClient, session: AsyncSession):
    user = User(
        email="existing@example.com",
        username="existing",
        first_name="Existing",
        last_name="User",
        password_hash="hash",
        is_admin=False,
    )
    session.add(user)
    await session.commit()

    resp = await client.post(
        "/api/auth/request-access",
        json={
            "email": "existing@example.com",
            "first_name": "Test",
            "last_name": "User",
        },
    )

    assert resp.status_code == EmailAlreadyRegistered.status_code
    body = resp.json()
    assert body["detail"] == EmailAlreadyRegistered.detail


async def test_request_access_pending(client: AsyncClient, session: AsyncSession):
    req = AccessRequest(
        email="pending@example.com",
        first_name="Pending",
        last_name="User",
        status=AccessRequestStatus.PENDING,
    )
    session.add(req)
    await session.commit()

    resp = await client.post(
        "/api/auth/request-access",
        json={
            "email": "pending@example.com",
            "first_name": "Test",
            "last_name": "User",
        },
    )

    assert resp.status_code == AccessRequestPending.status_code
    body = resp.json()
    assert body["detail"] == AccessRequestPending.detail


async def test_request_access_rejected(client: AsyncClient, session: AsyncSession):
    req = AccessRequest(
        email="rejected@example.com",
        first_name="Rejected",
        last_name="User",
        status=AccessRequestStatus.REJECTED,
    )
    session.add(req)
    await session.commit()

    resp = await client.post(
        "/api/auth/request-access",
        json={
            "email": "rejected@example.com",
            "first_name": "Test",
            "last_name": "User",
        },
    )

    assert resp.status_code == AccessRequestRejected.status_code
    body = resp.json()
    assert body["detail"] == AccessRequestRejected.detail
