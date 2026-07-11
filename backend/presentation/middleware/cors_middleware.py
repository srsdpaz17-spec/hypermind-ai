"""CORS middleware configuration."""

from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware

from app.config.settings import settings


def register_cors_middleware(app: FastAPI) -> None:
    """Attach configurable CORS middleware to the FastAPI application."""
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.CORS_ORIGINS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
