"""
Base domain exceptions for HyperMind AI.

Domain exceptions are pure business-logic errors, framework-agnostic,
and are translated to HTTP responses at the presentation layer
(see presentation/exception_handlers/error_responses.py).
"""

from typing import Any, Optional


class DomainException(Exception):
    """Base class for all domain-level exceptions."""

    default_message: str = "A domain error occurred."

    def __init__(
        self,
        message: Optional[str] = None,
        *,
        details: Optional[dict[str, Any]] = None,
    ) -> None:
        self.message = message or self.default_message
        self.details = details or {}
        super().__init__(self.message)


class EntityNotFoundException(DomainException):
    """Raised when a requested entity cannot be found."""

    default_message = "The requested entity was not found."

    def __init__(
        self,
        entity_name: Optional[str] = None,
        entity_id: Optional[Any] = None,
        *,
        details: Optional[dict[str, Any]] = None,
    ) -> None:
        message = self.default_message
        if entity_name is not None:
            message = f"{entity_name} not found"
            if entity_id is not None:
                message += f" (id={entity_id})"
        super().__init__(message, details=details)


class BusinessRuleViolationException(DomainException):
    """Raised when an operation violates a business rule/invariant."""

    default_message = "A business rule was violated."


class AuthenticationException(DomainException):
    """Raised when authentication fails (invalid credentials, expired token)."""

    default_message = "Authentication failed."


class AuthorizationException(DomainException):
    """Raised when an authenticated user lacks permission for an action."""

    default_message = "You are not authorized to perform this action."
