"""
Tenant entities (shared `public` schema).

Per ADR-002 (Multi-Tenancy Strategy - Schema Isolation), the `tenants` table
lives in the shared `public` schema and holds one row per organization,
including the name of the dedicated Postgres schema used for that tenant's
business data. `tenant_users` maps system users to the tenants they belong
to, together with their tenant-scoped role.
"""

from __future__ import annotations

import uuid
from typing import Any, Optional

from sqlalchemy import Boolean, ForeignKey, String, UniqueConstraint
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from domain.entities.base import BaseEntity


class Tenant(BaseEntity):
    """An organization (tenant) using the HyperMind platform."""

    __tablename__ = "tenants"
    __table_args__ = {"schema": "public"}

    name: Mapped[str] = mapped_column(String(255), nullable=False)
    slug: Mapped[str] = mapped_column(String(100), unique=True, nullable=False, index=True)
    schema_name: Mapped[str] = mapped_column(
        String(100), unique=True, nullable=False
    )
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    plan_type: Mapped[str] = mapped_column(
        String(50), default="trial", nullable=False
    )
    settings: Mapped[dict[str, Any]] = mapped_column(
        JSONB, default=dict, nullable=False
    )

    tenant_users: Mapped[list["TenantUser"]] = relationship(
        "TenantUser", back_populates="tenant", cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:  # pragma: no cover - debug helper
        return f"<Tenant id={self.id} slug={self.slug!r}>"


class TenantUser(BaseEntity):
    """Maps a system user to a tenant, with a tenant-scoped role.

    `user_id` intentionally does not carry a foreign key here: the user
    record itself lives inside the tenant's own schema (see
    `domain.entities.user.User`), so cross-schema FK constraints are not
    used. Referential integrity for `user_id` is enforced at the
    application layer.
    """

    __tablename__ = "tenant_users"
    __table_args__ = (
        UniqueConstraint("user_id", "tenant_id", name="uq_tenant_users_user_tenant"),
        {"schema": "public"},
    )

    user_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), nullable=False, index=True)
    tenant_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("public.tenants.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    role: Mapped[str] = mapped_column(String(50), default="member", nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    tenant: Mapped["Tenant"] = relationship("Tenant", back_populates="tenant_users")

    def __repr__(self) -> str:  # pragma: no cover - debug helper
        return f"<TenantUser user_id={self.user_id} tenant_id={self.tenant_id}>"
