from typing import Annotated

from fastapi import APIRouter, Depends

from app.core.dependencies import get_current_user
from app.models.schemas.user import UserPublic

api_router = APIRouter(prefix="/users", tags=["User"])


@api_router.get(
    "/current",
    operation_id="getCurrentUser",
)
def get_current_user_endpoint(
    user: Annotated[UserPublic, Depends(get_current_user)],
) -> UserPublic:
    return user
