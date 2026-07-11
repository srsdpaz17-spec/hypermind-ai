"""Employee entity (per-tenant schema).

Links a `User` to a `Company` with HR-specific attributes. Also supports
AI employees (`is_ai_employee=True`) which carry an `ai_config` JSONB blob
describing their agent configuration (see ADR / MODULE_SPECIFICATIONS for
the AI Kernel module).
"""

from __future__ import annotations

import uuid
from datetime import date
from typing import Any, Optional

from sqlalchemy import Boolean, Date, ForeignKey, String
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from domain.entities.base import BaseEntity


class Employee(BaseEntity):
    """An employee (human or AI) belonging to a company."""

    __tablename__ = "employees"

    user_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    company_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("companies.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    role: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    department: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    position: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    is_ai_employee: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    ai_config: Mapped[dict[str, Any]] = mapped_column(JSONB, default=dict, nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    hired_at: Mapped[Optional[date]] = mapped_column(Date, nullable=True)

    user: Mapped[Optional["User"]] = relationship("User", back_populates="employee")
    company: Mapped["Company"] = relationship("Company", back_populates="employees")

    def __repr__(self) -> str:  # pragma: no cover - debug helper
        return f"<Employee id={self.id} company_id={self.company_id}>"
