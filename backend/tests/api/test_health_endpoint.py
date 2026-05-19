from __future__ import annotations

import pytest

pytestmark = pytest.mark.api


def test_health_returns_200_with_status(client):
    response = client.get("/health")
    assert response.status_code == 200
    body = response.json()
    assert "status" in body
    assert "services" in body
    assert "storage" in body
    assert set(body["services"]) == {"inference_engine", "triage_model", "postgres", "minio", "spark"}


def test_health_ok_with_fakes(client):
    response = client.get("/health")
    assert response.json()["status"] == "ok"
