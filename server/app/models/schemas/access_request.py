from datetime import datetime
from typing import Literal

from pydantic import BaseModel

from app.models.enums import AccessRequestStatus


class ReviewerPublic(BaseModel):
    id: int
    username: str


class AccessRequestPublic(BaseModel):
    id: int
    email: str
    first_name: str
    last_name: str
    status: AccessRequestStatus
    reviewed_at: datetime | None
    reviewer: ReviewerPublic | None
    created_at: datetime
    updated_at: datetime


class UpdateAccessRequestStatusRequest(BaseModel):
    status: Literal[AccessRequestStatus.APPROVED, AccessRequestStatus.REJECTED]
