"""
Error handling middleware.

Acts as a final safety net that ensures any exception escaping the
route handlers (including ones not covered by the registered exception
handlers) is converted into a well-formed JSON 500 response instead of
leaking a raw traceback to clients.
"""

from collections.abc import Awaitable, Callable

from fastapi import FastAPI, Request, Response, status
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware

from app.config.logger import get_logger

logger = get_logger(__name__)


class ErrorHandlerMiddleware(BaseHTTPMiddleware):
    """Catches unhandled exceptions and returns a safe JSON error response."""

    async def dispatch(
        self, request: Request, call_next: Callable[[Request], Awaitable[Response]]
    ) -> Response:
        try:
            return await call_next(request)
        except Exception as exc:  # noqa: BLE001 - intentional catch-all safety net
            logger.error(
                "Unhandled exception caught by ErrorHandlerMiddleware",
                exc_info=exc,
                extra={"extra_fields": {"path": request.url.path}},
            )
            return JSONResponse(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                content={
                    "error": "InternalServerError",
                    "message": "An unexpected error occurred.",
                    "details": {},
                },
            )


def register_error_handler_middleware(app: FastAPI) -> None:
    """Attach the error handler middleware to the FastAPI application."""
    app.add_middleware(ErrorHandlerMiddleware)
