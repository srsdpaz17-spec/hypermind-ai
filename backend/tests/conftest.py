"""
Shared pytest fixtures for the backend test suite.

Ensures the `backend/` directory is on sys.path so that top-level
packages (app, domain, application, presentation, infrastructure) can be
imported regardless of the working directory pytest was invoked from.
"""

import sys
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

BACKEND_ROOT = Path(__file__).resolve().parent.parent
if str(BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(BACKEND_ROOT))

from app.main import app  # noqa: E402  (import after sys.path setup)


@pytest.fixture
def client() -> TestClient:
    """Provide a FastAPI TestClient with the app's lifespan events triggered."""
    with TestClient(app) as test_client:
        yield test_client
