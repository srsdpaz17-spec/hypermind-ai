from abc import abstractmethod

from domain.entities.role import Role
from domain.repositories.base_repository import BaseRepository


class RoleRepository(BaseRepository[Role]):

    @abstractmethod
    async def get_by_name(self, name: str):
        pass