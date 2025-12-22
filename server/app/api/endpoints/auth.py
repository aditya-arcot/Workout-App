import logging

from fastapi import APIRouter, BackgroundTasks, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import get_db
from app.models.schemas.auth import (
    RequestAccessRequest,
    RequestAccessResponse,
)
from app.services.auth import request_access
from app.services.email import EmailService, get_email_service

logger = logging.getLogger(__name__)

api_router = APIRouter(prefix="/auth")


@api_router.post("/request-access")
async def request_access_route(
    payload: RequestAccessRequest,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db),
    email_svc: EmailService = Depends(get_email_service),
) -> RequestAccessResponse:
    result = await request_access(
        first_name=payload.first_name,
        last_name=payload.last_name,
        email_svc=email_svc,
        background_tasks=background_tasks,
        db=db,
        email=payload.email,
    )
    already_approved, access_request = result.already_approved, result.access_request

    detail = ""
    if already_approved:
        detail = "Access request already approved. Approval email resent."
    else:
        detail = "Access request created. Please wait for admin approval."

    return RequestAccessResponse(
        detail=detail,
        access_request_id=access_request.id,
    )
