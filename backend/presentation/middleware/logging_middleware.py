"""
Request/response logging middleware.

Logs every incoming request and outgoing response with timing information
and a correlation ID (propagated via the X-Correlation-ID header, or
generated when absent). The correlation ID is stored in a context variable
so it is automatically included in all log records emitted while handling
the request (see app/config/logger.py).
"""

import time
import uuid
from collections.abc import Awaitable, Callable

from fastapi import FastAPI, Request, Response
from starlette.middleware.base import BaseHTTPMiddleware

from app.config.logger import correlation_id_ctx, get_logger

logger = get_logger(__name__)

CORRELATION_ID_HEADER = "X-Correlation-ID"


class LoggingMiddleware(BaseHTTPMiddleware):
    """Logs request/response pairs with timing and correlation IDs."""

    async def dispatch(
        self, request: Request, call_next: Callable[[Request], Awaitable[Response]]
    ) -> Response:
        correlation_id = request.headers.get(CORRELATION_ID_HEADER, str(uuid.uuid4()))
        token = correlation_id_ctx.set(correlation_id)

        start_time = time.perf_counter()
        logger.info(
            "Request started",
            extra={
                "extra_fields": {
                    "method": request.method,
                    "path": request.url.path,
                    "correlation_id": correlation_id,
                }
            },
        )

        try:
            response = await call_next(request)
        except Exception:
            duration_ms = round((time.perf_counter() - start_time) * 1000, 2)
            logger.error(
                "Request failed",
                extra={
                    "extra_fields": {
                        "method": request.method,
                        "path": request.url.path,
                        "duration_ms": duration_ms,
                        "correlation_id": correlation_id,
                    }
                },
            )
            raise
        finally:
            correlation_id_ctx.reset(token)

        duration_ms = round((time.perf_counter() - start_time) * 1000, 2)
        response.headers[CORRELATION_ID_HEADER] = correlation_id
        logger.info(
            "Request completed",
            extra={
                "extra_fields": {
                    "method": request.method,
                    "path": request.url.path,
                    "status_code": response.status_code,
                    "duration_ms": duration_ms,
                    "correlation_id": correlation_id,
                }
            },
        )
        return response


def register_logging_middleware(app: FastAPI) -> None:
    """Attach the request logging middleware to the FastAPI application."""
    app.add_middleware(LoggingMiddleware)
