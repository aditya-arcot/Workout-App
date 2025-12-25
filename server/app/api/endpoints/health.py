from fastapi import APIRouter

api_router = APIRouter(prefix="/health", tags=["Health"])


@api_router.get("", operation_id="getHealth")
def get_health_endpoint() -> str:
    return "ok"
