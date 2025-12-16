import logging

from fastapi import APIRouter, BackgroundTasks, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import get_db
from app.models.schemas.auth import (
    AccessRequestCreateRequest,
    AccessRequestCreateResponse,
)
from app.models.schemas.responses import ApiResponse
from app.services.auth import request_access
from app.services.email import EmailService, get_email_service

logger = logging.getLogger(__name__)

api_router = APIRouter(prefix="/auth")


@api_router.post("/request-access")
async def request_access_route(
    payload: AccessRequestCreateRequest,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db),
    email_svc: EmailService = Depends(get_email_service),
) -> ApiResponse[AccessRequestCreateResponse]:
    already_approved, access_request = await request_access(
        db=db,
        email=payload.email,
        first_name=payload.first_name,
        last_name=payload.last_name,
        email_svc=email_svc,
        background_tasks=background_tasks,
    )
    if already_approved:
        return ApiResponse(
            status="success",
            code="ACCESS_REQUEST_ALREADY_APPROVED",
            message="Access request already approved. Approval email resent.",
            data=AccessRequestCreateResponse(access_request_id=access_request.id),
        )
    return ApiResponse(
        status="success",
        code="ACCESS_REQUEST_CREATED",
        message="Access request created. Please wait for admin approval.",
        data=AccessRequestCreateResponse(access_request_id=access_request.id),
    )
