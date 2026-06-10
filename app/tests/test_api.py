"""Tests para la API FastAPI."""

from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_health():
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert data["service"] == "sw1-be-fastapi"


def test_health_method_not_allowed():
    response = client.post("/health")
    assert response.status_code == 405


def test_routing_predict_no_auth():
    """Sin header X-Internal-Key debe rechazar con 401."""
    response = client.post("/api/ai/routing-predict", json={})
    assert response.status_code == 401
    data = response.json()
    assert "detail" in data
