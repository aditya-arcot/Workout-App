from datetime import datetime

from pydantic import BaseModel


class JWTData(BaseModel):
    username: str


class UserPublic(BaseModel):
    id: int
    username: str
    email: str
    first_name: str
    last_name: str
    is_admin: bool
    created_at: datetime
    updated_at: datetime
