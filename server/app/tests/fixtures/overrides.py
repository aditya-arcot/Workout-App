import pytest

from app.core.config import (
    EmailSettings,
    settings,
)
from app.services.email import get_email_service


@pytest.fixture(autouse=True)
def override_env_test(monkeypatch: pytest.MonkeyPatch):
    original_env = settings.env

    monkeypatch.setattr(settings, "env", "test")
    yield

    monkeypatch.setattr(settings, "env", original_env)


@pytest.fixture
def override_email(monkeypatch: pytest.MonkeyPatch):
    original_email: EmailSettings = settings.email

    def _override(email: EmailSettings):
        monkeypatch.setattr(settings, "email", email)
        return get_email_service()

    yield _override

    monkeypatch.setattr(settings, "email", original_email)
