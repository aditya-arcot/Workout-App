from typing import Annotated

from fastapi import APIRouter, BackgroundTasks, Depends, Response, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.dependencies import get_db, refresh_token_cookie
from app.models.schemas.auth import LoginRequest, RegisterRequest, RequestAccessRequest
from app.models.schemas.errors import ErrorResponseModel
from app.services.auth import login, refresh, register, request_access
from app.services.email import EmailService, get_email_service

api_router = APIRouter(prefix="/auth", tags=["Auth"])


@api_router.post(
    "/request-access",
    operation_id="requestAccess",
    responses={
        status.HTTP_403_FORBIDDEN: ErrorResponseModel,
        status.HTTP_409_CONFLICT: ErrorResponseModel,
    },
)
async def request_access_endpoint(
    req: RequestAccessRequest,
    background_tasks: BackgroundTasks,
    db: Annotated[AsyncSession, Depends(get_db)],
    email_svc: Annotated[EmailService, Depends(get_email_service)],
) -> str:
    already_approved = await request_access(
        first_name=req.first_name,
        last_name=req.last_name,
        email_svc=email_svc,
        background_tasks=background_tasks,
        db=db,
        email=req.email,
    )
    if already_approved:
        return "Access already approved. Approval email resent"
    return "Requested access. Wait for admin approval"


@api_router.post(
    "/register",
    operation_id="register",
    status_code=status.HTTP_204_NO_CONTENT,
    responses={
        status.HTTP_400_BAD_REQUEST: ErrorResponseModel,
        status.HTTP_409_CONFLICT: ErrorResponseModel,
    },
)
async def register_endpoint(
    req: RegisterRequest,
    db: Annotated[AsyncSession, Depends(get_db)],
):
    await register(
        token_str=req.token,
        username=req.username,
        password=req.password,
        db=db,
    )


@api_router.post(
    "/login",
    operation_id="login",
    status_code=status.HTTP_204_NO_CONTENT,
    responses={
        status.HTTP_401_UNAUTHORIZED: ErrorResponseModel,
    },
)
async def login_endpoint(
    req: LoginRequest,
    db: Annotated[AsyncSession, Depends(get_db)],
    res: Response,
):
    result = await login(username=req.username, password=req.password, db=db)
    res.set_cookie(
        key="access_token",
        value=result.access_token,
        httponly=True,
        secure=settings.cookie_secure,
        samesite=settings.cookie_same_site,
        max_age=60 * 60,  # 1 hour
    )
    res.set_cookie(
        key="refresh_token",
        value=result.refresh_token,
        httponly=True,
        secure=settings.cookie_secure,
        samesite=settings.cookie_same_site,
        max_age=60 * 60 * 24 * 365,  # 1 year
    )


@api_router.post(
    "/refresh-token",
    operation_id="refreshToken",
    status_code=status.HTTP_204_NO_CONTENT,
    responses={
        status.HTTP_401_UNAUTHORIZED: ErrorResponseModel,
    },
)
async def refresh_token_endpoint(
    db: Annotated[AsyncSession, Depends(get_db)],
    refresh_token: Annotated[str, Depends(refresh_token_cookie)],
    res: Response,
):
    access_token = await refresh(db=db, token=refresh_token)
    res.set_cookie(
        key="access_token",
        value=access_token,
        httponly=True,
        secure=settings.cookie_secure,
        samesite=settings.cookie_same_site,
        max_age=60 * 60,  # 1 hour
    )


@api_router.post(
    "/logout",
    operation_id="logout",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def logout_endpoint(res: Response):
    res.delete_cookie(
        key="access_token",
        httponly=True,
        secure=settings.cookie_secure,
        samesite=settings.cookie_same_site,
    )
    res.delete_cookie(
        key="refresh_token",
        httponly=True,
        secure=settings.cookie_secure,
        samesite=settings.cookie_same_site,
    )
