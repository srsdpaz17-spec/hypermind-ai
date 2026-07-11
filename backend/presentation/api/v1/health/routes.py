"""
Health check endpoints.

Provides liveness/readiness information for orchestrators (Docker,
Kubernetes) and monitoring tools.
"""

from fastapi import APIRouter

from app.config.settings import settings

router = APIRouter(tags=["health"])


def _health_payload() -> dict[str, str]:
    return {
        "status": "healthy",
        "service": "hypermind-ai",
        "version": settings.APP_VERSION,
        "environment": settings.ENVIRONMENT,
    }


@router.get("/health")
async def health_root() -> dict[str, str]:
    """Root-level health check, useful for load balancers and Docker healthchecks."""
    return _health_payload()


@router.get("/api/v1/health")
async def health_v1() -> dict[str, str]:
    """Versioned health check endpoint under the v1 API namespace."""
    return _health_payload()
