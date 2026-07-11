"""
HyperMind AI - FastAPI application entry point.

Wires together configuration, middleware, exception handlers, and routers.
Manages application lifespan (startup/shutdown) for database and cache
connections.
"""

from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

from fastapi import FastAPI
from redis.asyncio import Redis

from app.config.database import dispose_engine
from app.config.logger import configure_logging, get_logger
from app.config.settings import settings

from presentation.api.v1.health.routes import router as health_router
from presentation.api.v1.auth.routes import router as auth_router

from presentation.exception_handlers.error_responses import (
    register_exception_handlers,
)

from presentation.middleware.cors_middleware import register_cors_middleware
from presentation.middleware.error_handler_middleware import (
    register_error_handler_middleware,
)
from presentation.middleware.logging_middleware import (
    register_logging_middleware,
)

configure_logging()
logger = get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """Manage startup and shutdown of shared resources (DB pool, Redis)."""

    logger.info("Starting HyperMind AI backend", extra={"extra_fields": {}})

    redis_client: Redis = Redis.from_url(
        settings.REDIS_URL,
        encoding="utf-8",
        decode_responses=True,
    )

    app.state.redis = redis_client

    try:
        await redis_client.ping()
        logger.info("Redis connection established")
    except Exception as exc:
        logger.warning(f"Redis connection failed at startup: {exc}")

    yield

    logger.info("Shutting down HyperMind AI backend")

    await redis_client.close()
    await dispose_engine()


def create_app() -> FastAPI:
    """Application factory."""

    app = FastAPI(
        title=settings.APP_NAME,
        version=settings.APP_VERSION,
        description="HyperMind AI - Enterprise AI Operating System backend",
        debug=settings.DEBUG,
        lifespan=lifespan,
    )

    # Middleware
    register_error_handler_middleware(app)
    register_logging_middleware(app)
    register_cors_middleware(app)

    # Exception Handlers
    register_exception_handlers(app)

    # Routers
    app.include_router(health_router)
    app.include_router(auth_router)

    return app


app = create_app()