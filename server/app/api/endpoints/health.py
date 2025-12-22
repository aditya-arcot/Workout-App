from fastapi import APIRouter

api_router = APIRouter()


@api_router.get("/health")
def get_health_route() -> str:
    return "ok"
