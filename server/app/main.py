import logging

from fastapi import FastAPI

from .api.health import router as health_router
from .core.config import settings
from .core.logging import setup_logging

logger = logging.getLogger(__name__)

setup_logging(level=settings.LOG_LEVEL, file_log=settings.ENV == "dev")

logger.debug("Logging initialized")
logger.debug("Settings loaded: %s", settings.model_dump())


def create_app() -> FastAPI:
    app = FastAPI()
    app.include_router(health_router)
    return app


logger.info("Starting app...")
app = create_app()
