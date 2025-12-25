from typing import Annotated

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import get_current_admin, get_db
from app.services.admin import get_access_requests

api_router = APIRouter(
    prefix="/admin", tags=["Admin"], dependencies=[Depends(get_current_admin)]
)


@api_router.get("/access-requests", operation_id="getAccessRequests")
async def get_access_requests_endpoint(db: Annotated[AsyncSession, Depends(get_db)]):
    return await get_access_requests(db)
