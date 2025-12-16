from typing import Callable
from unittest.mock import patch

import pytest
from _pytest.logging import LogCaptureFixture

from app.core.config import settings
from app.services.email import EmailService, get_email_service


@pytest.fixture
def override_email_backend(monkeypatch: pytest.MonkeyPatch):
    original_backend = settings.EMAIL_BACKEND

    def _override(backend: str):
        monkeypatch.setattr(settings, "EMAIL_BACKEND", backend)
        return get_email_service()

    yield _override

    monkeypatch.setattr(settings, "EMAIL_BACKEND", original_backend)


@pytest.mark.asyncio
async def test_console_backend(
    override_email_backend: Callable[[str], EmailService], caplog: LogCaptureFixture
):
    service = override_email_backend("console")
    caplog.set_level("INFO")
    await service.send("user@example.com", "Subject", "Body")
    assert any("EMAIL (console)" in r.message for r in caplog.records)


@pytest.mark.asyncio
async def test_disabled_backend(
    override_email_backend: Callable[[str], EmailService], caplog: LogCaptureFixture
):
    service = override_email_backend("disabled")
    caplog.set_level("DEBUG")
    await service.send("user@example.com", "Subject", "Body")
    assert any("skipping" in r.message for r in caplog.records)


@pytest.mark.asyncio
async def test_smtp_backend(override_email_backend: Callable[[str], EmailService]):
    service = override_email_backend("smtp")
    with patch("aiosmtplib.send") as mock_send:
        await service.send("user@example.com", "Test SMTP", "Body")
        mock_send.assert_called_once()
