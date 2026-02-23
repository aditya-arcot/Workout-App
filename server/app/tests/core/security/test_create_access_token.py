from datetime import datetime, timezone

import jwt

from app.core.config import Settings
from app.core.security import create_access_jwt


def test_create_access_token(settings: Settings):
    token = create_access_jwt(settings.admin.username, settings)

    assert isinstance(token, str)
    assert len(token) > 0

    payload = jwt.decode(
        token,
        settings.jwt.secret_key,
        algorithms=[settings.jwt.algorithm],
    )

    assert payload["sub"] == settings.admin.username
    assert "exp" in payload
    exp = datetime.fromtimestamp(payload["exp"], tz=timezone.utc)
    assert exp > datetime.now(timezone.utc)
