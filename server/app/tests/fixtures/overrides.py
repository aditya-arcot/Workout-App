import pytest

from app.core.config import (
    EmailSettings,
    get_settings,
)
from app.services.email import get_email_service


@pytest.fixture(autouse=True)
def override_env_test(monkeypatch: pytest.MonkeyPatch):
    original_env = get_settings().env

    monkeypatch.setattr(get_settings(), "env", "test")
    yield

    monkeypatch.setattr(get_settings(), "env", original_env)


@pytest.fixture
def override_email(monkeypatch: pytest.MonkeyPatch):
    original_email: EmailSettings = get_settings().email

    def _override(email: EmailSettings):
        monkeypatch.setattr(get_settings(), "email", email)
        return get_email_service()

    yield _override

    monkeypatch.setattr(get_settings(), "email", original_email)
