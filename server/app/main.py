import logging

from fastapi import FastAPI
from fastapi.concurrency import asynccontextmanager
from starlette.exceptions import HTTPException as StarletteHTTPException
from starlette.middleware.cors import CORSMiddleware

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
    fastapi_app = FastAPI(
        title=title,
        lifespan=lifespan,
        docs_url=None,
        redoc_url=None,
    )
else:
    fastapi_app = FastAPI(
        title=title,
        lifespan=lifespan,
    )

fastapi_app.add_exception_handler(StarletteHTTPException, exception_handler)
fastapi_app.add_exception_handler(Exception, exception_handler)
fastapi_app.include_router(api_router, prefix="/api")

# CORS headers are not included in error responses when using add_middleware for CORSMiddleware
# https://github.com/fastapi/fastapi/discussions/8027#discussioncomment-5146484
app = CORSMiddleware(
    app=fastapi_app,
    allow_origins=settings.cors_urls,
    allow_credentials=True,
    allow_methods=["*"],
)
