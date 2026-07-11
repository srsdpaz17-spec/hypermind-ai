from datetime import datetime, timedelta
from jose import jwt

from app.config.settings import settings


class JWTService:

    @staticmethod
    def create_access_token(data: dict):

        payload = data.copy()

        payload["exp"] = datetime.utcnow() + timedelta(
            minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
        )

        return jwt.encode(
            payload,
            settings.JWT_SECRET_KEY,
            algorithm=settings.JWT_ALGORITHM
        )

    @staticmethod
    def create_refresh_token(data: dict):

        payload = data.copy()

        payload["exp"] = datetime.utcnow() + timedelta(
            days=settings.REFRESH_TOKEN_EXPIRE_DAYS
        )

        return jwt.encode(
            payload,
            settings.JWT_SECRET_KEY,
            algorithm=settings.JWT_ALGORITHM
        )

    @staticmethod
    def decode(token: str):

        return jwt.decode(
            token,
            settings.JWT_SECRET_KEY,
            algorithms=[settings.JWT_ALGORITHM]
        )