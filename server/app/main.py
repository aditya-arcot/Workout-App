import logging

from fastapi import FastAPI

from .api import api_router
from .core.config import settings
from .core.logging import setup_logging

logger = logging.getLogger(__name__)

setup_logging(level=settings.LOG_LEVEL, file_log=settings.ENV == "dev")

logger.debug("Logging initialized")
logger.debug("Settings loaded: %s", settings.model_dump())


def create_app() -> FastAPI:
    app = FastAPI()
    app.include_router(api_router, prefix="/api")
    return app


logger.info("Starting app...")
app = create_app()
