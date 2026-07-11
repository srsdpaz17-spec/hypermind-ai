"""Tests for the health check endpoints."""

from fastapi.testclient import TestClient


def test_health_root(client: TestClient) -> None:
    """GET /health should return a healthy status payload."""
    response = client.get("/health")

    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "healthy"
    assert body["service"] == "hypermind-ai"
    assert "version" in body
    assert "environment" in body


def test_health_v1(client: TestClient) -> None:
    """GET /api/v1/health should return the same healthy status payload."""
    response = client.get("/api/v1/health")

    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "healthy"
    assert body["service"] == "hypermind-ai"


def test_docs_available(client: TestClient) -> None:
    """GET /docs should serve the Swagger UI."""
    response = client.get("/docs")

    assert response.status_code == 200
