import logging

from fastapi import FastAPI
from fastapi.concurrency import asynccontextmanager
from fastapi.middleware.cors import CORSMiddleware

from .api import api_router
from .core.config import settings
from .core.handlers import exception_handler
from .core.logging import setup_logging

logger = logging.getLogger(__name__)


def create_directories():
    settings.DATA_DIR.mkdir(parents=True, exist_ok=True)
    settings.LOG_DIR.mkdir(parents=True, exist_ok=True)


@asynccontextmanager
async def lifespan(_: FastAPI):
    create_directories()
    setup_logging()
    logger.debug("Initialized logging")
    logger.debug("Loaded settings: %s", settings.model_dump())
    logger.info("Starting app...")
    yield


title = "RepTrack"
if settings.ENV != "prod":
    title += f" ({settings.ENV})"

if settings.IS_PROD:
    app = FastAPI(title=title, lifespan=lifespan, docs_url=None, redoc_url=None)
else:
    app = FastAPI(title=title, lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_URLS,
    allow_credentials=True,
    allow_methods=["*"],
)
app.add_exception_handler(Exception, exception_handler)
app.include_router(api_router, prefix="/api")
