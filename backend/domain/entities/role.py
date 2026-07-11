"""RBAC entities (per-tenant schema): Role, Permission, and their
many-to-many association tables (per ADR-006).
"""

from __future__ import annotations

import uuid
from datetime import datetime
from typing import Any, Optional

from sqlalchemy import Boolean, DateTime, ForeignKey, String, Text
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func

from domain.entities.base import BaseEntity, UUIDMixin
from app.config.database import Base


class Role(BaseEntity):
    """A named collection of permissions assignable to users."""

    __tablename__ = "roles"

    name: Mapped[str] = mapped_column(String(100), unique=True, nullable=False, index=True)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    is_system_role: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    permissions: Mapped[dict[str, Any]] = mapped_column(JSONB, default=dict, nullable=False)

    role_permissions: Mapped[list["RolePermission"]] = relationship(
        "RolePermission", back_populates="role", cascade="all, delete-orphan"
    )
    user_roles: Mapped[list["UserRole"]] = relationship(
        "UserRole", back_populates="role", cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:  # pragma: no cover - debug helper
        return f"<Role id={self.id} name={self.name!r}>"


class Permission(UUIDMixin, Base):
    """A granular permission, e.g. `users.read` (resource=users, action=read)."""

    __tablename__ = "permissions"

    name: Mapped[str] = mapped_column(String(150), unique=True, nullable=False, index=True)
    resource: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    action: Mapped[str] = mapped_column(String(50), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    role_permissions: Mapped[list["RolePermission"]] = relationship(
        "RolePermission", back_populates="permission", cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:  # pragma: no cover - debug helper
        return f"<Permission name={self.name!r}>"


class RolePermission(Base):
    """Association table linking roles to permissions (composite PK)."""

    __tablename__ = "role_permissions"

    role_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("roles.id", ondelete="CASCADE"), primary_key=True
    )
    permission_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("permissions.id", ondelete="CASCADE"),
        primary_key=True,
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    role: Mapped["Role"] = relationship("Role", back_populates="role_permissions")
    permission: Mapped["Permission"] = relationship(
        "Permission", back_populates="role_permissions"
    )

    def __repr__(self) -> str:  # pragma: no cover - debug helper
        return f"<RolePermission role_id={self.role_id} permission_id={self.permission_id}>"


class UserRole(Base):
    """Association table linking users to roles (composite PK)."""

    __tablename__ = "user_roles"

    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), primary_key=True
    )
    role_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("roles.id", ondelete="CASCADE"), primary_key=True
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    user: Mapped["User"] = relationship("User", back_populates="user_roles")
    role: Mapped["Role"] = relationship("Role", back_populates="user_roles")

    def __repr__(self) -> str:  # pragma: no cover - debug helper
        return f"<UserRole user_id={self.user_id} role_id={self.role_id}>"
