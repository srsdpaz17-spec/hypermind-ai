"""
Domain entities package.

Exposes all SQLAlchemy ORM models so that a single `import domain.entities`
(or importing this package) is enough to populate `Base.metadata` for
Alembic autogeneration and `Base.metadata.create_all()`.
"""

from domain.entities.base import BaseEntity, TenantMixin, TimestampMixin, UUIDMixin
from domain.entities.tenant import Tenant, TenantUser
from domain.entities.user import User
from domain.entities.company import Company
from domain.entities.employee import Employee
from domain.entities.role import Permission, Role, RolePermission, UserRole
from domain.entities.auth import RefreshToken
from domain.entities.audit import AuditLog

__all__ = [
    "BaseEntity",
    "TenantMixin",
    "TimestampMixin",
    "UUIDMixin",
    "Tenant",
    "TenantUser",
    "User",
    "Company",
    "Employee",
    "Role",
    "Permission",
    "RolePermission",
    "UserRole",
    "RefreshToken",
    "AuditLog",
]
