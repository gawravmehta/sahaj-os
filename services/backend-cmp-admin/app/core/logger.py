import logging
from logging.handlers import RotatingFileHandler
import os
import sys
import json
from datetime import datetime, UTC
from app.core.config import settings


class JsonFormatter(logging.Formatter):
    def format(self, record):

        log_record = {
            "@timestamp": datetime.now(UTC).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
        }

        allowed_attrs = [
            "module",
            "lineno",
            "funcName",
            "process",
            "processName",
        ]

        for attr in allowed_attrs:
            value = getattr(record, attr, None)
            if value is not None:
                log_record[attr] = value

        if record.exc_info:
            log_record["exception"] = self.formatException(record.exc_info)

        for key, value in record.__dict__.items():
            if key not in [
                "msg",
                "args",
                "levelname",
                "levelno",
                "name",
                "module",
                "lineno",
                "funcName",
                "process",
                "processName",
                "pathname",
                "filename",
                "stack_info",
                "thread",
                "threadName",
                "msecs",
                "relativeCreated",
                "created",
                "exc_info",
                "exc_text",
            ]:
                log_record[key] = value
        return json.dumps(log_record, default=str)


def setup_logging(log_file_path: str = "logs/app.log"):
    """
    Initialize logging once per process.
    FastAPI calls this in lifespan()
    Workers call this at startup.
    """
    parent_logger = logging.getLogger(settings.SERVICE_NAME)

    if getattr(parent_logger, "_setup_complete", False):
        return parent_logger

    log_level = logging.INFO
    parent_logger.setLevel(log_level)
    parent_logger.propagate = False

    os.makedirs(os.path.dirname(log_file_path), exist_ok=True)

    file_handler = RotatingFileHandler(log_file_path, maxBytes=10 * 1024 * 1024, backupCount=5)
    file_handler.setLevel(log_level)
    file_handler.setFormatter(JsonFormatter())
    parent_logger.addHandler(file_handler)

    if settings.ENVIRONMENT == "dev":
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(log_level)
        console_handler.setFormatter(logging.Formatter("%(asctime)s - %(levelname)s - %(name)s - %(message)s"))
        parent_logger.addHandler(console_handler)

    parent_logger._setup_complete = True

    parent_logger.info("Logging initialized", extra={"service": "logger"})

    return parent_logger


def get_logger(name: str):
    """
    Returns a child logger.
    Example: get_logger("api") -> cmp_admin_backend.api
    """
    parent = logging.getLogger(settings.SERVICE_NAME)
    return parent.getChild(name)


app_logger = logging.getLogger(settings.SERVICE_NAME)
