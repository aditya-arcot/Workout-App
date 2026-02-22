from datetime import datetime, timezone

import jwt

from app.core.config import get_settings
from app.core.security import create_access_jwt


def test_create_access_token():
    token = create_access_jwt(get_settings().admin.username)

    assert isinstance(token, str)
    assert len(token) > 0

    payload = jwt.decode(
        token,
        get_settings().jwt.secret_key,
        algorithms=[get_settings().jwt.algorithm],
    )

    assert payload["sub"] == get_settings().admin.username
    assert "exp" in payload
    exp = datetime.fromtimestamp(payload["exp"], tz=timezone.utc)
    assert exp > datetime.now(timezone.utc)
