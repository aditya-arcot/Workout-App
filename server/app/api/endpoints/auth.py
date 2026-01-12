from typing import Annotated

from fastapi import APIRouter, BackgroundTasks, Depends, Response, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.dependencies import get_db
from app.models.schemas.auth import (
    LoginRequest,
    RequestAccessRequest,
    RequestAccessResponse,
)
from app.services.auth import login, request_access
from app.services.email import EmailService, get_email_service

api_router = APIRouter(prefix="/auth", tags=["Auth"])


@api_router.post("/request-access", operation_id="requestAccess")
async def request_access_endpoint(
    payload: RequestAccessRequest,
    background_tasks: BackgroundTasks,
    db: Annotated[AsyncSession, Depends(get_db)],
    email_svc: Annotated[EmailService, Depends(get_email_service)],
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


@api_router.post(
    "/login",
    operation_id="login",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def login_endpoint(
    payload: LoginRequest,
    db: Annotated[AsyncSession, Depends(get_db)],
    response: Response,
):
    token = await login(username=payload.username, password=payload.password, db=db)
    response.set_cookie(
        key="access_token",
        value=token,
        httponly=True,
        # must be False for pytest in test env
        secure=settings.ENV != "test",
        samesite=settings.COOKIE_SAME_SITE,
        max_age=60 * 60,  # 1 hour
    )


@api_router.post(
    "/logout",
    operation_id="logout",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def logout_endpoint(response: Response):
    response.delete_cookie(
        key="access_token",
        httponly=True,
        samesite=settings.COOKIE_SAME_SITE,
    )
