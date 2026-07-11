from __future__ import annotations

from abc import abstractmethod
from uuid import UUID

from domain.entities.user import User
from domain.repositories.base_repository import BaseRepository


class UserRepository(BaseRepository[User]):

    @abstractmethod
    async def get_by_email(self, email: str) -> User | None:
        ...

    @abstractmethod
    async def email_exists(self, email: str) -> bool:
        ...

    @abstractmethod
    async def activate(self, user_id: UUID) -> bool:
        ...

    @abstractmethod
    async def deactivate(self, user_id: UUID) -> bool:
        ...

    @abstractmethod
    async def verify_email(self, user_id: UUID) -> bool:
        ...

    @abstractmethod
    async def update_last_login(self, user_id: UUID) -> None:
        ...