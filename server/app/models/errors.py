class DomainError(Exception):
    code: str
    message: str
    http_status: int

    def __init__(self, message: str | None = None):
        if message:
            self.message = message
        super().__init__(self.message)
