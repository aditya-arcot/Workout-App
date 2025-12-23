from fastapi import APIRouter

from .endpoints.admin import api_router as admin_router
from .endpoints.auth import api_router as auth_router
from .endpoints.health import api_router as health_router
from .endpoints.user import api_router as user_router

api_router = APIRouter()
api_router.include_router(admin_router)
api_router.include_router(auth_router)
api_router.include_router(health_router)
api_router.include_router(user_router)
