from fastapi import APIRouter

from .endpoints.health import api_router as health_router

api_router = APIRouter()
api_router.include_router(health_router, tags=["Health"])
