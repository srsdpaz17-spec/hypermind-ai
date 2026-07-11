"""
Application configuration management.
"""

from functools import lru_cache
from typing import List

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore",
    )

    # ======================
    # Application
    # ======================
    APP_NAME: str = "HyperMind AI"
    APP_VERSION: str = "1.0.0"
    ENVIRONMENT: str = "development"
    DEBUG: bool = True

    # ======================
    # Database
    # ======================
    DATABASE_URL: str = (
        "postgresql+asyncpg://hypermind:hypermind_dev@localhost:5432/hypermind"
    )
    DATABASE_POOL_SIZE: int = 10
    DATABASE_MAX_OVERFLOW: int = 20
    DATABASE_POOL_TIMEOUT: int = 30
    DATABASE_ECHO: bool = False

    # ======================
    # Redis
    # ======================
    REDIS_URL: str = "redis://localhost:6379/0"

    # ======================
    # JWT
    # ======================
    JWT_SECRET_KEY: str = "change-me-in-production-please"
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 15
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    # ======================
    # CORS
    # ======================
    CORS_ORIGINS: str | List[str] = Field(
        default="http://localhost:3000,http://localhost:8000"
    )

    @field_validator("CORS_ORIGINS", mode="after")
    @classmethod
    def parse_cors(cls, value):
        if isinstance(value, str):
            return [
                origin.strip()
                for origin in value.split(",")
                if origin.strip()
            ]
        return value

    # ======================
    # Logging
    # ======================
    LOG_LEVEL: str = "INFO"

    @property
    def is_production(self) -> bool:
        return self.ENVIRONMENT.lower() == "production"


@lru_cache
def get_settings():
    return Settings()


settings = get_settings()
