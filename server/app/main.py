import logging

from fastapi import FastAPI

from .api import api_router
from .core.config import settings
from .core.handlers import exception_handler
from .core.logging import setup_logging

logger = logging.getLogger(__name__)

setup_logging()

logger.debug("Logging initialized")
logger.debug("Settings loaded: %s", settings.model_dump())


def create_app() -> FastAPI:
    app = FastAPI()
    app.add_exception_handler(Exception, exception_handler)
    app.include_router(api_router, prefix="/api")
    return app


logger.info("Starting app...")
app = create_app()
