from __future__ import annotations

import pytest

pytestmark = pytest.mark.api


def test_prometheus_endpoint_returns_text(client):
    response = client.get("/metrics/prom")
    assert response.status_code == 200
    assert "text/plain" in response.headers["content-type"]


def test_prometheus_endpoint_records_triage(client):
    # Trigger a triage so the counter increments
    client.post("/triage", json={"symptoms": ["chest pain"]})
    response = client.get("/metrics/prom")
    body = response.text
    assert "hospital_http_requests_total" in body
    assert "hospital_triage_assessments_total" in body
