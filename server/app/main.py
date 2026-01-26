import logging

from fastapi import FastAPI
from fastapi.concurrency import asynccontextmanager
from fastapi.middleware.cors import CORSMiddleware
from starlette.exceptions import HTTPException as StarletteHTTPException

from .api import api_router
from .core.config import settings
from .core.handlers import exception_handler
from .core.logging import setup_logging

logger = logging.getLogger(__name__)


def create_directories():
    settings.data_dir.mkdir(parents=True, exist_ok=True)
    settings.log_dir.mkdir(parents=True, exist_ok=True)


@asynccontextmanager
async def lifespan(_: FastAPI):
    create_directories()
    setup_logging()
    logger.debug("Initialized logging")
    logger.debug("Loaded settings: %s", settings.model_dump())
    logger.info("Starting app...")
    yield


title = settings.repo_name
if settings.env != "prod":
    title += f" ({settings.env})"

if settings.is_prod:
    app = FastAPI(
        title=title,
        lifespan=lifespan,
        docs_url=None,
        redoc_url=None,
    )
else:
    app = FastAPI(
        title=title,
        lifespan=lifespan,
    )

app.add_middleware(
    CORSMiddleware,  # ty:ignore[invalid-argument-type]
    allow_origins=settings.cors_urls,
    allow_credentials=True,
    allow_methods=["*"],
)
app.add_exception_handler(StarletteHTTPException, exception_handler)
app.add_exception_handler(Exception, exception_handler)
app.include_router(api_router, prefix="/api")
