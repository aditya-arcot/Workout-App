import logging
import logging.config
from typing import Any

from pythonjsonlogger.json import JsonFormatter

from app.core.config import settings


def setup_logging() -> None:
    handlers: dict[str, dict[str, Any]] = {
        "console": {
            "class": "logging.StreamHandler",
            "formatter": "json",
        },
    }

    log_file = settings.log_dir / f"reptrack_server_{settings.env}.log"
    handlers["file"] = {
        "class": "logging.handlers.RotatingFileHandler",
        "formatter": "json",
        "filename": str(log_file),
        "encoding": "utf-8",
        "maxBytes": 1024 * 1024,  # 1 MiB
        "backupCount": 5,
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
                "level": settings.log_level.upper(),
                "handlers": list(handlers.keys()),
            },
        }
    )
