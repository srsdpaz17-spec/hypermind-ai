"""Domain exceptions package."""

from domain.exceptions.domain_exception import (
    DomainException,
    EntityNotFoundException,
    BusinessRuleViolationException,
    AuthenticationException,
    AuthorizationException,
)

__all__ = [
    "DomainException",
    "EntityNotFoundException",
    "BusinessRuleViolationException",
    "AuthenticationException",
    "AuthorizationException",
]
