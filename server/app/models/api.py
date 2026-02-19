from dataclasses import dataclass

REQUEST_ACCESS_APPROVED_MESSAGE = "Access already approved. Approval email resent"
REQUEST_ACCESS_CREATED_MESSAGE = "Requested access. Wait for admin approval"


@dataclass
class LoginResult:
    access_token: str
    refresh_token: str
