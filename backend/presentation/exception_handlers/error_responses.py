"""
Maps domain exceptions to standardized HTTP JSON error responses, and
registers global exception handlers on the FastAPI application.
"""

import logging
from typing import Any

from fastapi import FastAPI, Request, status
from fastapi.encoders import jsonable_encoder
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from domain.exceptions.domain_exception import (
    AuthenticationException,
    AuthorizationException,
    BusinessRuleViolationException,
    DomainException,
    EntityNotFoundException,
)

logger = logging.getLogger(__name__)

_EXCEPTION_STATUS_MAP: dict[type[DomainException], int] = {
    EntityNotFoundException: status.HTTP_404_NOT_FOUND,
    BusinessRuleViolationException: status.HTTP_422_UNPROCESSABLE_ENTITY,
    AuthenticationException: status.HTTP_401_UNAUTHORIZED,
    AuthorizationException: status.HTTP_403_FORBIDDEN,
}


def _build_error_body(
    *, error: str, message: str, details: dict[str, Any] | None = None
) -> dict[str, Any]:
    return {
        "error": error,
        "message": message,
        "details": details or {},
    }


def _resolve_status_code(exc: DomainException) -> int:
    for exc_type, status_code in _EXCEPTION_STATUS_MAP.items():
        if isinstance(exc, exc_type):
            return status_code
    return status.HTTP_400_BAD_REQUEST


async def domain_exception_handler(
    request: Request, exc: DomainException
) -> JSONResponse:
    """Handle any DomainException subclass raised during request processing."""
    status_code = _resolve_status_code(exc)
    logger.warning(
        "Domain exception handled",
        extra={
            "extra_fields": {
                "path": request.url.path,
                "exception_type": type(exc).__name__,
                "status_code": status_code,
            }
        },
    )
    return JSONResponse(
        status_code=status_code,
        content=_build_error_body(
            error=type(exc).__name__,
            message=exc.message,
            details=exc.details,
        ),
    )


async def validation_exception_handler(
    request: Request, exc: RequestValidationError
) -> JSONResponse:
    """Handle FastAPI/Pydantic request validation errors."""
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content=_build_error_body(
            error="ValidationError",
            message="Request validation failed.",
            details={"errors": jsonable_encoder(exc.errors())},
        ),
    )


async def unhandled_exception_handler(
    request: Request, exc: Exception
) -> JSONResponse:
    """Catch-all handler for any unexpected, unhandled exception."""
    logger.error(
        "Unhandled exception",
        exc_info=exc,
        extra={"extra_fields": {"path": request.url.path}},
    )
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content=_build_error_body(
            error="InternalServerError",
            message="An unexpected error occurred.",
        ),
    )


def register_exception_handlers(app: FastAPI) -> None:
    """Register all global exception handlers on the FastAPI app instance."""
    app.add_exception_handler(DomainException, domain_exception_handler)
    app.add_exception_handler(RequestValidationError, validation_exception_handler)
    app.add_exception_handler(Exception, unhandled_exception_handler)
