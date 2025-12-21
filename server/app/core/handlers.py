import logging

from fastapi import Request
from fastapi.responses import JSONResponse

from app.models.errors import HttpError
from app.models.schemas.responses import ApiResponse

logger = logging.getLogger(__name__)


async def http_exception_handler(
    request: Request,
    err: Exception,
):
    # only called for HttpError
    assert isinstance(err, HttpError)
    resp: ApiResponse[None] = ApiResponse(
        status="error" if err.http_status >= 400 else "success",
        code=err.code,
        message=err.message,
        data=None,
    )
    logger.info(f"Handled HttpError: {err.code} - {err.message}")
    return JSONResponse(
        status_code=err.http_status,
        content=resp.model_dump(),
    )
