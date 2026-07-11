"""Audit log entity (per-tenant schema).

Records every sensitive state change for compliance (GDPR/LGPD, ADR-003 /
SECURITY_ARCHITECTURE OWASP #10). `old_values`/`new_values` capture a
before/after snapshot of the affected resource as JSON.
"""

from __future__ import annotations

import uuid
from typing import Any, Optional

from sqlalchemy import String
from sqlalchemy.dialects.postgresql import INET, JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column

from domain.entities.base import BaseEntity


class AuditLog(BaseEntity):
    """An immutable record of an action performed within a tenant."""

    __tablename__ = "audit_logs"

    user_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True), nullable=True, index=True
    )
    action: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    resource_type: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    resource_id: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    old_values: Mapped[Optional[dict[str, Any]]] = mapped_column(JSONB, nullable=True)
    new_values: Mapped[Optional[dict[str, Any]]] = mapped_column(JSONB, nullable=True)
    ip_address: Mapped[Optional[str]] = mapped_column(INET, nullable=True)
    user_agent: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)

    def __repr__(self) -> str:  # pragma: no cover - debug helper
        return f"<AuditLog id={self.id} action={self.action!r} resource_type={self.resource_type!r}>"
