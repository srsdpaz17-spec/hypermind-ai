from __future__ import annotations

from typing import Any, Generic, TypeVar

from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession

T = TypeVar("T")


class BaseRepository(Generic[T]):
    """
    Implementação base utilizando SQLAlchemy Async.
    """

    def __init__(self, session: AsyncSession, model: type[T]):
        self.session = session
        self.model = model

    async def create(self, entity: T) -> T:
        self.session.add(entity)
        await self.session.flush()
        await self.session.refresh(entity)
        return entity

    async def get_by_id(self, entity_id: Any) -> T | None:
        result = await self.session.execute(
            select(self.model).where(self.model.id == entity_id)
        )
        return result.scalar_one_or_none()

    async def list(
        self,
        skip: int = 0,
        limit: int = 100,
    ) -> list[T]:
        result = await self.session.execute(
            select(self.model)
            .offset(skip)
            .limit(limit)
        )

        return list(result.scalars().all())

    async def update(self, entity: T) -> T:
        await self.session.flush()
        await self.session.refresh(entity)
        return entity

    async def delete(self, entity_id: Any) -> bool:
        result = await self.session.execute(
            delete(self.model).where(self.model.id == entity_id)
        )

        return result.rowcount > 0

    async def exists(self, entity_id: Any) -> bool:
        return await self.get_by_id(entity_id) is not None