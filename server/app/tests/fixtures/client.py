from typing import AsyncGenerator

import pytest
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import (
    AsyncConnection,
    AsyncSession,
    AsyncTransaction,
)

from app.core.dependencies import get_db
from app.main import fastapi_app
from app.services.email import EmailService, get_email_service


@pytest.fixture(scope="session")
def anyio_backend():
    return "asyncio"


@pytest.fixture()
async def client(
    connection: AsyncConnection,
    transaction: AsyncTransaction,
    mock_email_svc: EmailService,
) -> AsyncGenerator[AsyncClient, None]:
    async def override_get_db() -> AsyncGenerator[AsyncSession, None]:
        async_session = AsyncSession(
            bind=connection,
            join_transaction_mode="create_savepoint",
        )
        async with async_session:
            yield async_session

    fastapi_app.dependency_overrides[get_db] = override_get_db
    fastapi_app.dependency_overrides[get_email_service] = lambda: mock_email_svc
    try:
        yield AsyncClient(
            transport=ASGITransport(app=fastapi_app), base_url="http://test"
        )
    finally:
        del fastapi_app.dependency_overrides[get_db]
        del fastapi_app.dependency_overrides[get_email_service]

        await transaction.rollback()
