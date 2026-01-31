import logging

from fastapi import Request
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException

from app.core.config import settings

logger = logging.getLogger(__name__)


async def exception_handler(request: Request, exc: Exception):
    if isinstance(exc, StarletteHTTPException):
        logger.error(f"HTTP error: {exc.status_code} - {exc.detail}")

        if isinstance(exc.detail, dict):
            # pass through custom HTTPError
            content = exc.detail

        else:
            detail = "HTTP Error"
            if (not settings.is_prod) and exc.detail:
                detail = exc.detail

            content = {
                "detail": detail,
                "code": "http_error",
            }

        return JSONResponse(
            status_code=exc.status_code,
            content=content,
        )

    logger.exception(f"Unhandled error: {exc}")

    detail = "Internal Server Error"
    if (not settings.is_prod) and exc.args and exc.args[0]:
        detail = exc.args[0]

    return JSONResponse(
        status_code=500,
        content={
            "detail": detail,
            "code": "internal_server_error",
        },
    )
