from pydantic import BaseModel, EmailStr


class AccessRequestCreateRequest(BaseModel):
    email: EmailStr
    first_name: str
    last_name: str


class AccessRequestCreateResponse(BaseModel):
    access_request_id: int
