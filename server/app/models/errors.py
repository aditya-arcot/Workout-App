from fastapi import HTTPException, status


class HTTPError(HTTPException):
    status_code: int
    code: str
    detail: str

    def __init__(self):
        if not hasattr(self, "code"):
            raise RuntimeError(f"{self.__class__.__name__} must define code")

        super().__init__(
            status_code=self.status_code,
            detail={
                "code": self.code,
                "detail": self.detail,
            },
        )


class EmailAlreadyRegistered(HTTPError):
    status_code = status.HTTP_409_CONFLICT
    code = "email_already_registered"
    detail = "This email is already registered. Please log in."


class AccessRequestPending(HTTPError):
    status_code = status.HTTP_409_CONFLICT
    code = "access_request_pending"
    detail = "An access request for this email is already pending"


class AccessRequestRejected(HTTPError):
    status_code = status.HTTP_403_FORBIDDEN
    code = "access_request_rejected"
    detail = "An access request for this email was previously rejected"


class InvalidCredentials(HTTPError):
    status_code = status.HTTP_401_UNAUTHORIZED
    code = "invalid_credentials"
    detail = "Invalid credentials"


class InsufficientPermissions(HTTPError):
    status_code = status.HTTP_403_FORBIDDEN
    code = "insufficient_permissions"
    detail = "Insufficient permissions"
