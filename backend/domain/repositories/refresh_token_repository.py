from abc import abstractmethod

from domain.entities.auth import RefreshToken
from domain.repositories.base_repository import BaseRepository


class RefreshTokenRepository(BaseRepository[RefreshToken]):

    @abstractmethod
    async def get_by_token(self, token: str):
        pass