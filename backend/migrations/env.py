"""
Alembic migration environment.

Async-compatible: uses SQLAlchemy's async engine + `run_sync` bridge so
migrations run against the same asyncpg driver as the application
(see `app/config/database.py`).

Imports `domain.entities` so that every ORM model is registered on
`Base.metadata` before Alembic inspects it (required for autogenerate).

Multi-tenancy (ADR-002): most tables in this project's metadata belong to
a *tenant* schema (no explicit `schema=` — they rely on the connection's
`search_path`/`schema_translate_map`), while a few shared tables
(`tenants`, `tenant_users`) are explicitly pinned to the `public` schema.
To run this migration against a specific tenant schema, pass
`-x schema=<schema_name>` on the alembic CLI; it defaults to `public`
for the initial bootstrap (system tables + template tenant schema).
"""

from __future__ import annotations

import asyncio
from logging.config import fileConfig

from alembic import context
from sqlalchemy import pool
from sqlalchemy.engine import Connection
from sqlalchemy.ext.asyncio import AsyncEngine, create_async_engine

# --- Make `backend/` importable regardless of CWD ---------------------------
import sys
from pathlib import Path

BACKEND_ROOT = Path(__file__).resolve().parent.parent
if str(BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(BACKEND_ROOT))

from app.config.database import Base  # noqa: E402
from app.config.settings import settings  # noqa: E402

# Import every entity module so their models register on Base.metadata.
import domain.entities  # noqa: E402,F401

# Alembic Config object, provides access to values in alembic.ini.
config = context.config

# Interpret the config file for Python logging.
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# Metadata object used for autogenerate support.
target_metadata = Base.metadata

# Tenant schema to target. Defaults to "public" (shared tables +
# initial bootstrap). Override with: alembic upgrade head -x schema=tenant_acme
TENANT_SCHEMA = context.get_x_argument(as_dictionary=True).get("schema", "public")


def get_database_url() -> str:
    """Read the database URL from application settings (never hardcoded)."""
    return settings.DATABASE_URL


def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode (emits SQL without a DB connection)."""
    url = get_database_url()
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        version_table_schema=TENANT_SCHEMA,
        include_schemas=True,
    )

    with context.begin_transaction():
        context.run_migrations()


def do_run_migrations(connection: Connection) -> None:
    context.configure(
        connection=connection,
        target_metadata=target_metadata,
        version_table_schema=TENANT_SCHEMA,
        include_schemas=True,
        compare_type=True,
    )

    with context.begin_transaction():
        context.run_migrations()


async def run_async_migrations() -> None:
    """Create an async engine and run migrations via the sync-style API."""
    connectable: AsyncEngine = create_async_engine(
        get_database_url(),
        poolclass=pool.NullPool,
    )

    async with connectable.connect() as connection:
        await connection.run_sync(do_run_migrations)

    await connectable.dispose()


def run_migrations_online() -> None:
    """Run migrations in 'online' mode using the async engine."""
    asyncio.run(run_async_migrations())


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
