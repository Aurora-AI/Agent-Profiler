import pytest
from fastapi.testclient import TestClient
from src.app.main import app

client = TestClient(app)

def test_profiling_endpoint_valid():
    payload = {"agent_id": "Agent-007"}
    response = client.post("/profiling/analyze", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["agent_id"] == "Agent-007"
    assert "profile" in data
    assert 0.0 <= data["profile"]["risk_tolerance"] <= 1.0

def test_profiling_endpoint_determinism():
    # Same ID should yield same results
    payload = {"agent_id": "FixedSeed"}
    resp1 = client.post("/profiling/analyze", json=payload).json()
    resp2 = client.post("/profiling/analyze", json=payload).json()
    assert resp1 == resp2

def test_profiling_validation():
    # Missing required field
    response = client.post("/profiling/analyze", json={})
    assert response.status_code == 422
