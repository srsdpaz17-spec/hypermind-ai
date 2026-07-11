"""
PostgreSQL connection infrastructure.

Thin wrapper around the async engine/session factory defined in
app/config/database.py, exposed here so infrastructure-layer repository
implementations depend on `infrastructure.persistence.postgres` rather than
reaching into the `app` package directly.
"""

from collections.abc import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession

from app.config.database import AsyncSessionLocal, Base, engine

__all__ = ["Base", "engine", "AsyncSessionLocal", "get_session"]


async def get_session() -> AsyncGenerator[AsyncSession, None]:
    """Yield a new database session for use within infrastructure components."""
    async with AsyncSessionLocal() as session:
        yield session
