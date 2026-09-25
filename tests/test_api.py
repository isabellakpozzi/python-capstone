from fastapi.testclient import TestClient
from api.main import app

client = TestClient(app)


def test_health_endpoint_returns_200():
    response = client.get("/health")
    assert response.status_code == 200
    assert "status" in response.json()


def test_query_endpoint_returns_valid_response(monkeypatch):
    response = client.post("/query", json={"query": "What is our security policy?"})
    assert response.status_code == 200
    body = response.json()
    assert body["type"] in ("qualitative", "quantitative", "complex", "ambiguous", "unsupported")
    assert "response" in body


def test_query_endpoint_rejects_malformed_request():
    response = client.post("/query", json={"wrong_field": "oops"})
    assert response.status_code == 422  