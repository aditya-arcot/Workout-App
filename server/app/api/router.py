from fastapi import APIRouter

from .endpoints.auth import api_router as auth_router
from .endpoints.health import api_router as health_router

api_router = APIRouter()
api_router.include_router(auth_router, tags=["Auth"])
api_router.include_router(health_router, tags=["Health"])
