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

# New Tests for Error Mapping
def test_rate_limit_error_mapping():
    # We can mock the service to raise the error
    from src.app.main import service
    from src.domain.interfaces import QuotaExceededError
    from unittest.mock import patch

    with patch.object(service, 'generate', side_effect=QuotaExceededError("rate", 429, "Limit")):
        payload = {
            "provider_name": "mock",
            "prompt": "Limit",
            "config": {}
        }
        response = client.post("/generate", json=payload)
        assert response.status_code == 429
        assert "Rate limit exceeded" in response.json()['detail']

def test_circuit_breaker_error_mapping():
    from src.app.main import service
    from src.services.circuit_breaker_service import CircuitBreakerOpenError
    from unittest.mock import patch

    with patch.object(service, 'generate', side_effect=CircuitBreakerOpenError("cb", 503, "Open")):
        payload = {
            "provider_name": "mock",
            "prompt": "Break",
            "config": {}
        }
        response = client.post("/generate", json=payload)
        assert response.status_code == 503
        assert "Circuit Open" in response.json()['detail']
