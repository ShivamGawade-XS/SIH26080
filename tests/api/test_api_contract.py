"""
API Contract and Endpoint Tests for FastAPI Backend.
"""

import pytest
from fastapi.testclient import TestClient

from varsha.api.app import app


@pytest.fixture
def client():
    return TestClient(app)


def test_healthz_endpoint(client):
    response = client.get("/healthz")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert "Varsha" in data["system"]


def test_meta_endpoint(client):
    response = client.get("/api/v1/meta")
    assert response.status_code == 200
    data = response.json()
    assert "data_mode" in data
    assert "available_runs" in data


def test_runs_list_endpoint(client):
    response = client.get("/api/v1/runs")
    assert response.status_code == 200
    assert isinstance(response.json(), list)


def test_verification_summary_endpoint(client):
    response = client.get("/api/v1/verification/summary")
    assert response.status_code == 200
    data = response.json()
    assert "ladder" in data
    assert "B0_Raw" in data["ladder"]
