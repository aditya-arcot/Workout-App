from unittest.mock import AsyncMock

import pytest

from app.services.email import EmailService
from app.services.github import GitHubService


@pytest.fixture
def mock_email_svc():
    service = AsyncMock(spec=EmailService)
    service.send_access_request_notification = AsyncMock()
    service.send_access_request_approved_email = AsyncMock()
    service.send_access_request_rejected_email = AsyncMock()
    service.send_password_reset_email = AsyncMock()
    return service


@pytest.fixture
def mock_github_svc():
    service = AsyncMock(spec=GitHubService)
    service.create_feedback_issue = AsyncMock()
    return service
