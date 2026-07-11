from abc import abstractmethod

from domain.entities.company import Company
from domain.repositories.base_repository import BaseRepository


class CompanyRepository(BaseRepository[Company]):

    @abstractmethod
    async def get_by_slug(self, slug: str):
        pass