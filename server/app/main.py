import logging

from fastapi import FastAPI

from .api import api_router
from .core.config import settings
from .core.handlers import exception_handler
from .core.logging import setup_logging

if __name__ == "__main__":
    logger = logging.getLogger(__name__)

    setup_logging()

    logger.debug("Initialized logging")
    logger.debug("Loaded settings: %s", settings.model_dump())

    logger.info("Starting app")

app = FastAPI()
app.add_exception_handler(Exception, exception_handler)
app.include_router(api_router, prefix="/api")
