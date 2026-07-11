"""
Seed script: bootstraps the default tenant, its schema, RBAC roles,
permissions, and an initial admin user.

Usage (from `backend/`):
    python -m scripts.seed

What it does:
1. Creates (or reuses) the default tenant `HyperMind Demo` in
   `public.tenants`.
2. Creates the tenant's dedicated Postgres schema and the per-tenant
   tables inside it (mirrors `migrations/versions/001_initial_schema.py`
   table set, scoped via `schema_translate_map`).
3. Seeds default permissions (`users.read`, `users.write`, ... etc.).
4. Seeds `SuperAdmin`, `Admin`, and `User` roles, wiring `SuperAdmin` to
   every permission.
5. Creates an admin user (admin@hypermind.ai / admin123), assigns it the
   `SuperAdmin` role, and links it to the tenant via `public.tenant_users`.

Idempotent: safe to run multiple times (uses "does it already exist"
checks before inserting).
"""

from __future__ import annotations

import asyncio
import sys
import uuid
from pathlib import Path

BACKEND_ROOT = Path(__file__).resolve().parent.parent
if str(BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(BACKEND_ROOT))

from passlib.context import CryptContext
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from app.config.database import Base, engine
from app.config.logger import get_logger
from domain.entities.role import Permission, Role, RolePermission, UserRole
from domain.entities.tenant import Tenant, TenantUser
from domain.entities.user import User

logger = get_logger(__name__)

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

DEFAULT_TENANT_NAME = "HyperMind Demo"
DEFAULT_TENANT_SLUG = "hypermind-demo"
DEFAULT_TENANT_SCHEMA = "tenant_hypermind_demo"

ADMIN_EMAIL = "admin@hypermind.ai"
ADMIN_PASSWORD = "admin123"

DEFAULT_PERMISSIONS: list[tuple[str, str, str, str]] = [
    # (name, resource, action, description)
    ("users.read", "users", "read", "View user accounts"),
    ("users.write", "users", "write", "Create and update user accounts"),
    ("users.delete", "users", "delete", "Delete user accounts"),
    ("companies.read", "companies", "read", "View companies"),
    ("companies.write", "companies", "write", "Create and update companies"),
    ("companies.delete", "companies", "delete", "Delete companies"),
    ("employees.read", "employees", "read", "View employees"),
    ("employees.write", "employees", "write", "Create and update employees"),
    ("employees.delete", "employees", "delete", "Delete employees"),
    ("roles.read", "roles", "read", "View roles and permissions"),
    ("roles.write", "roles", "write", "Create and update roles"),
    ("audit_logs.read", "audit_logs", "read", "View audit logs"),
]


async def create_tenant_schema(schema_name: str) -> None:
    """Create the tenant's dedicated Postgres schema if it doesn't exist,
    then create all per-tenant tables inside it."""
    async with engine.begin() as conn:
        await conn.exec_driver_sql(f'CREATE SCHEMA IF NOT EXISTS "{schema_name}"')

        def create_tenant_tables(sync_conn):
            tenant_conn = sync_conn.execution_options(
                schema_translate_map={None: schema_name}
            )
            tenant_only_metadata_tables = [
                table
                for table in Base.metadata.sorted_tables
                if table.schema != "public"
            ]
            Base.metadata.create_all(
                bind=tenant_conn, tables=tenant_only_metadata_tables
            )

        await conn.run_sync(create_tenant_tables)


async def ensure_tenant() -> Tenant:
    async with AsyncSession(engine) as session:
        result = await session.execute(
            select(Tenant).where(Tenant.slug == DEFAULT_TENANT_SLUG)
        )
        tenant = result.scalar_one_or_none()
        if tenant is not None:
            logger.info(f"Tenant '{DEFAULT_TENANT_SLUG}' already exists")
            return tenant

        tenant = Tenant(
            name=DEFAULT_TENANT_NAME,
            slug=DEFAULT_TENANT_SLUG,
            schema_name=DEFAULT_TENANT_SCHEMA,
            is_active=True,
            plan_type="enterprise",
            settings={},
        )
        session.add(tenant)
        await session.commit()
        await session.refresh(tenant)
        logger.info(f"Created tenant '{DEFAULT_TENANT_SLUG}'")
        return tenant


def tenant_session_factory(schema_name: str) -> async_sessionmaker[AsyncSession]:
    """Return a session factory whose connections translate the default
    (None) schema to the given tenant schema, so unqualified table names
    (users, roles, ...) resolve inside that tenant's schema."""
    tenant_engine = engine.execution_options(
        schema_translate_map={None: schema_name}
    )
    return async_sessionmaker(bind=tenant_engine, expire_on_commit=False)


async def seed_permissions(session: AsyncSession) -> dict[str, Permission]:
    permissions: dict[str, Permission] = {}
    for name, resource, action, description in DEFAULT_PERMISSIONS:
        result = await session.execute(
            select(Permission).where(Permission.name == name)
        )
        permission = result.scalar_one_or_none()
        if permission is None:
            permission = Permission(
                name=name, resource=resource, action=action, description=description
            )
            session.add(permission)
            await session.flush()
            logger.info(f"Created permission '{name}'")
        permissions[name] = permission
    return permissions


async def seed_roles(
    session: AsyncSession, permissions: dict[str, Permission]
) -> dict[str, Role]:
    roles_spec = {
        "SuperAdmin": {
            "description": "Full, unrestricted access to all resources.",
            "is_system_role": True,
            "permission_names": list(permissions.keys()),
        },
        "Admin": {
            "description": "Administrative access to manage the tenant.",
            "is_system_role": True,
            "permission_names": [
                "users.read",
                "users.write",
                "companies.read",
                "companies.write",
                "employees.read",
                "employees.write",
                "roles.read",
            ],
        },
        "User": {
            "description": "Standard user with read-only access.",
            "is_system_role": True,
            "permission_names": ["users.read", "companies.read", "employees.read"],
        },
    }

    roles: dict[str, Role] = {}
    for role_name, spec in roles_spec.items():
        result = await session.execute(select(Role).where(Role.name == role_name))
        role = result.scalar_one_or_none()
        if role is None:
            role = Role(
                name=role_name,
                description=spec["description"],
                is_system_role=spec["is_system_role"],
                permissions={"names": spec["permission_names"]},
            )
            session.add(role)
            await session.flush()
            logger.info(f"Created role '{role_name}'")

        existing = await session.execute(
            select(RolePermission.permission_id).where(
                RolePermission.role_id == role.id
            )
        )
        existing_permission_ids = {row[0] for row in existing.all()}
        for permission_name in spec["permission_names"]:
            permission = permissions[permission_name]
            if permission.id not in existing_permission_ids:
                session.add(
                    RolePermission(role_id=role.id, permission_id=permission.id)
                )

        roles[role_name] = role

    await session.flush()
    return roles


async def seed_admin_user(session: AsyncSession, superadmin_role: Role) -> User:
    result = await session.execute(select(User).where(User.email == ADMIN_EMAIL))
    user = result.scalar_one_or_none()
    if user is None:
        user = User(
            email=ADMIN_EMAIL,
            password_hash=pwd_context.hash(ADMIN_PASSWORD),
            first_name="Admin",
            last_name="User",
            is_active=True,
            is_verified=True,
        )
        session.add(user)
        await session.flush()
        logger.info(f"Created admin user '{ADMIN_EMAIL}'")

    existing_link = await session.execute(
        select(UserRole).where(
            UserRole.user_id == user.id, UserRole.role_id == superadmin_role.id
        )
    )
    if existing_link.scalar_one_or_none() is None:
        session.add(UserRole(user_id=user.id, role_id=superadmin_role.id))

    return user


async def link_user_to_tenant(tenant_id: uuid.UUID, user_id: uuid.UUID) -> None:
    async with AsyncSession(engine) as session:
        result = await session.execute(
            select(TenantUser).where(
                TenantUser.tenant_id == tenant_id, TenantUser.user_id == user_id
            )
        )
        link = result.scalar_one_or_none()
        if link is None:
            session.add(
                TenantUser(
                    tenant_id=tenant_id,
                    user_id=user_id,
                    role="owner",
                    is_active=True,
                )
            )
            await session.commit()
            logger.info("Linked admin user to default tenant (public.tenant_users)")


async def run_seed() -> None:
    logger.info("Seeding HyperMind AI database...")

    tenant = await ensure_tenant()

    logger.info(f"Ensuring schema '{tenant.schema_name}' and tenant tables exist...")
    await create_tenant_schema(tenant.schema_name)

    session_factory = tenant_session_factory(tenant.schema_name)
    async with session_factory() as session:
        permissions = await seed_permissions(session)
        roles = await seed_roles(session, permissions)
        admin_user = await seed_admin_user(session, roles["SuperAdmin"])
        await session.commit()
        admin_user_id = admin_user.id

    await link_user_to_tenant(tenant.id, admin_user_id)

    logger.info("Seed complete.")
    logger.info(f"Default tenant: {DEFAULT_TENANT_SLUG} (schema={tenant.schema_name})")
    logger.info(f"Admin login: {ADMIN_EMAIL} / {ADMIN_PASSWORD}")


def main() -> None:
    asyncio.run(run_seed())


if __name__ == "__main__":
    main()
