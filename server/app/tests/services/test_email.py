from typing import Callable
from unittest.mock import patch

import pytest
from _pytest.logging import LogCaptureFixture

from app.core.config import (
    EmailConsoleSettings,
    EmailDisabledSettings,
    EmailSmtpSettings,
)
from app.services.email import EmailService


@pytest.mark.asyncio
async def test_smtp(
    override_email: Callable[[EmailSmtpSettings], EmailService],
):
    smtp_settings = EmailSmtpSettings(
        backend="smtp",
        email_from="test@example.com",
        smtp_host="smtp.example.com",
        smtp_username="user",
        smtp_password="pass",
    )
    service = override_email(smtp_settings)
    with patch("aiosmtplib.send") as mock_send:
        await service.send("user@example.com", "Test SMTP", "Body")
        mock_send.assert_called_once()


@pytest.mark.asyncio
async def test_console(
    override_email: Callable[[EmailConsoleSettings], EmailService],
    caplog: LogCaptureFixture,
):
    console_settings = EmailConsoleSettings(backend="console")
    service = override_email(console_settings)
    caplog.set_level("INFO")
    await service.send("user@example.com", "Subject", "Body")
    assert any("EMAIL (console)" in r.message for r in caplog.records)


@pytest.mark.asyncio
async def test_disabled(
    override_email: Callable[[EmailDisabledSettings], EmailService],
    caplog: LogCaptureFixture,
):
    disabled_settings = EmailDisabledSettings(backend="disabled")
    service = override_email(disabled_settings)
    caplog.set_level("DEBUG")
    await service.send("user@example.com", "Subject", "Body")
    assert any("skipping" in r.message for r in caplog.records)
