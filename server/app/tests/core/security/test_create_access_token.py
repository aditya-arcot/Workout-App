from datetime import datetime, timezone

import jwt

from app.core.config import settings
from app.core.security import create_access_token


def test_create_access_token():
    token = create_access_token(settings.ADMIN_USERNAME)

    assert isinstance(token, str)
    assert len(token) > 0

    payload = jwt.decode(
        token,
        settings.JWT_SECRET_KEY,
        algorithms=[settings.ALGORITHM],
    )

    assert payload["sub"] == settings.ADMIN_USERNAME
    assert "exp" in payload
    exp = datetime.fromtimestamp(payload["exp"], tz=timezone.utc)
    assert exp > datetime.now(timezone.utc)
