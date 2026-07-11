from __future__ import annotations

from sqlalchemy.ext.asyncio import AsyncSession

from domain.entities.user import User
from infrastructure.repositories.postgres.user_repository import UserRepository
from infrastructure.security.password_service import PasswordService
from presentation.api.v1.auth.schemas.register import RegisterRequest


class RegisterUseCase:

    def __init__(self, db: AsyncSession):
        self.db = db
        self.users = UserRepository(db)

    async def execute(self, request: RegisterRequest) -> User:

        if await self.users.email_exists(request.email):
            raise ValueError("E-mail já cadastrado.")

        user = User(
            first_name=request.first_name,
            last_name=request.last_name,
            email=request.email.lower(),
            password_hash=PasswordService.hash_password(request.password),
            is_active=True,
            is_verified=False,
        )

        await self.users.create(user)

        return user