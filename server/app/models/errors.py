class DomainError(Exception):
    code: str
    message: str
    http_status: int

    def __init__(self, message: str | None = None):
        if message:
            self.message = message
        super().__init__(self.message)


class EmailAlreadyRegistered(DomainError):
    code = "EMAIL_ALREADY_REGISTERED"
    message = "This email is already registered. Please log in."
    http_status = 409


class AccessRequestPending(DomainError):
    code = "ACCESS_REQUEST_PENDING"
    message = "An access request for this email is already pending"
    http_status = 409


class AccessRequestRejected(DomainError):
    code = "ACCESS_REQUEST_REJECTED"
    message = "An access request for this email was previously rejected"
    http_status = 403
