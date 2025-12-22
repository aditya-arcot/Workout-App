from fastapi import HTTPException, status


class HTTPError(HTTPException):
    status_code: int
    detail: str

    def __init__(self):
        super().__init__(
            status_code=self.status_code,
            detail=self.detail,
        )


class EmailAlreadyRegistered(HTTPError):
    status_code = status.HTTP_409_CONFLICT
    detail = "This email is already registered. Please log in."


class AccessRequestPending(HTTPError):
    status_code = status.HTTP_409_CONFLICT
    detail = "An access request for this email is already pending"


class AccessRequestRejected(HTTPError):
    status_code = status.HTTP_403_FORBIDDEN
    detail = "An access request for this email was previously rejected"
