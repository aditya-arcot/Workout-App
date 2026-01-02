import logging
import logging.config
from pathlib import Path

from pythonjsonlogger.json import JsonFormatter

from app.core.config import settings

LOG_DIR = Path.home() / "Projects" / "Logs"
LOG_FILE = LOG_DIR / f"reptrack_server_{settings.ENV}.log"


def setup_logging() -> None:
    handlers = {
        "console": {
            "class": "logging.StreamHandler",
            "formatter": "json",
        },
    }

    LOG_DIR.mkdir(parents=True, exist_ok=True)
    handlers["file"] = {
        "class": "logging.FileHandler",
        "formatter": "json",
        "filename": str(LOG_FILE),
        "encoding": "utf-8",
    }

    logging.config.dictConfig(
        {
            "version": 1,
            "disable_existing_loggers": False,
            "formatters": {
                "json": {
                    "()": JsonFormatter,
                    "fmt": ("%(asctime)s %(levelname)s %(name)s %(message)s"),
                    "rename_fields": {
                        "asctime": "time",
                        "levelname": "level",
                        "name": "logger",
                    },
                },
            },
            "handlers": handlers,
            "root": {
                "level": settings.LOG_LEVEL,
                "handlers": list(handlers.keys()),
            },
        }
    )
