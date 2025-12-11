import pytest
from fastapi.testclient import TestClient
from src.app.main import app

client = TestClient(app)

def test_health_check():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}

def test_generate_endpoint():
    payload = {
        "provider_name": "mock",
        "prompt": "Hello API",
        "config": {
            "response_delay": 0.0,
            "mock_response": "API Response"
        }
    }
    response = client.post("/generate", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["content"] == "API Response"

def test_generate_endpoint_validation_error():
    payload = {
        "provider_name": "mock",
        # Missing prompt
        "config": {}
    }
    response = client.post("/generate", json=payload)
    assert response.status_code == 422 # Pydantic validation error
