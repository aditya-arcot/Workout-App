from pydantic import BaseModel, EmailStr


class RequestAccessRequest(BaseModel):
    email: EmailStr
    first_name: str
    last_name: str


class RequestAccessResponse(BaseModel):
    detail: str
    access_request_id: int
