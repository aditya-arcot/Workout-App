from fastapi import APIRouter

from app.models.schemas.responses import ApiResponse

api_router = APIRouter()


@api_router.get("/health")
def health() -> ApiResponse[None]:
    return ApiResponse(status="success", code="HEALTH_OK", message="ok", data=None)
