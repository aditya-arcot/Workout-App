import logging
from typing import Any, Callable

import pytest
from pydantic_settings import SettingsConfigDict
from pytest import MonkeyPatch

from app.core.config import Settings
from app.models.schemas.config import EmailSmtpSettings
from app.services.email import EmailService, get_email_service
from app.tests.fixtures.settings import TEST_SETTINGS

logger = logging.getLogger(__name__)


@pytest.fixture(autouse=True)
def disable_env_file(monkeypatch: MonkeyPatch):
    monkeypatch.setattr(
        Settings,
        "model_config",
        SettingsConfigDict(extra="ignore"),
    )


@pytest.fixture
def override_settings() -> Callable[[], Settings]:
    def _factory(**overrides: dict[str, Any]) -> Settings:
        settings = TEST_SETTINGS.model_copy(update=overrides)
        return settings

    return _factory


@pytest.fixture
def override_email_settings() -> Callable[[EmailSmtpSettings], EmailService]:
    def _factory(email_settings: EmailSmtpSettings) -> EmailService:
        settings: Settings = TEST_SETTINGS.model_copy(update={"email": email_settings})
        service: EmailService = get_email_service(settings)
        return service

    return _factory
