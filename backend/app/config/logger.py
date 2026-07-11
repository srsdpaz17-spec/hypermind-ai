"""
Structured JSON logging configuration.

Provides a JSON formatter that includes timestamp, level, message,
correlation_id and tenant_id (when available via context variables),
and a get_logger() factory for consistent logger creation across the app.
"""

import json
import logging
import sys
from contextvars import ContextVar
from datetime import datetime, timezone
from typing import Any, Optional

from app.config.settings import settings

# Context variables populated by the logging middleware per-request.
correlation_id_ctx: ContextVar[Optional[str]] = ContextVar(
    "correlation_id", default=None
)
tenant_id_ctx: ContextVar[Optional[str]] = ContextVar("tenant_id", default=None)


class JSONFormatter(logging.Formatter):
    """Formats log records as single-line JSON objects."""

    def format(self, record: logging.LogRecord) -> str:
        payload: dict[str, Any] = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "level": record.levelname,
            "message": record.getMessage(),
            "logger": record.name,
            "correlation_id": correlation_id_ctx.get(),
            "tenant_id": tenant_id_ctx.get(),
        }

        if record.exc_info:
            payload["exception"] = self.formatException(record.exc_info)

        extra_fields = getattr(record, "extra_fields", None)
        if isinstance(extra_fields, dict):
            payload.update(extra_fields)

        return json.dumps(payload, default=str)


def configure_logging() -> None:
    """Configure the root logger and uvicorn loggers to emit JSON logs."""
    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(JSONFormatter())

    root_logger = logging.getLogger()
    root_logger.handlers = [handler]
    root_logger.setLevel(settings.LOG_LEVEL)

    for logger_name in ("uvicorn", "uvicorn.error", "uvicorn.access"):
        uvicorn_logger = logging.getLogger(logger_name)
        uvicorn_logger.handlers = [handler]
        uvicorn_logger.propagate = False
        uvicorn_logger.setLevel(settings.LOG_LEVEL)


def get_logger(name: str) -> logging.Logger:
    """Factory function returning a named logger configured for JSON output."""
    return logging.getLogger(name)
