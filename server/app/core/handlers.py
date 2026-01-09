import logging

from fastapi import Request
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException

logger = logging.getLogger(__name__)


async def exception_handler(request: Request, exc: Exception):
    if isinstance(exc, StarletteHTTPException):
        logger.exception(f"HTTP exception: {exc.status_code} - {exc.detail}")
        return JSONResponse(
            status_code=exc.status_code,
            content={"detail": exc.detail},
        )

    if exc.args and exc.args[0]:
        message = exc.args[0]
    else:
        message = "Internal Server Error"

    logger.exception(f"Non-HTTP exception - {message}")
    return JSONResponse(
        status_code=500,
        content={"detail": message},
    )
