from __future__ import annotations

from datetime import datetime
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from domain.entities.user import User
from domain.repositories.user_repository import UserRepository as IUserRepository
from infrastructure.repositories.postgres.base_repository import BaseRepository


class UserRepository(BaseRepository[User], IUserRepository):

    def __init__(self, session: AsyncSession):
        super().__init__(session, User)

    async def get_by_email(self, email: str) -> User | None:
        result = await self.session.execute(
            select(User).where(User.email == email)
        )
        return result.scalar_one_or_none()

    async def exists(self, email: str) -> bool:
        return await self.get_by_email(email) is not None

    async def activate(self, user_id: UUID) -> bool:
        user = await self.get_by_id(user_id)

        if not user:
            return False

        user.is_active = True
        await self.update(user)

        return True

    async def deactivate(self, user_id: UUID) -> bool:
        user = await self.get_by_id(user_id)

        if not user:
            return False

        user.is_active = False
        await self.update(user)

        return True

    async def verify_email(self, user_id: UUID) -> bool:
        user = await self.get_by_id(user_id)

        if not user:
            return False

        user.is_verified = True
        await self.update(user)

        return True

    async def update_last_login(self, user_id: UUID) -> None:
        user = await self.get_by_id(user_id)

        if user:
            user.last_login_at = datetime.utcnow()
            await self.update(user)