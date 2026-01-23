from dataclasses import dataclass

from app.models.database.access_request import AccessRequest


@dataclass
class RequestAccessResult:
    already_approved: bool
    access_request: AccessRequest


@dataclass
class LoginResult:
    access_token: str
    refresh_token: str
