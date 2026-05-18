from __future__ import annotations

from app.services.dashboard_data import DashboardDataService
from tests.helpers.fakes import FakeBackendClient


def test_snapshot_falls_back_to_defaults():
    backend = FakeBackendClient()
    snapshot = DashboardDataService(backend).snapshot()
    assert snapshot["backend_status"] == "no disponible"
    assert snapshot["metrics"]["radiology"]["total_studies"] == 0
    assert snapshot["recent_studies"] == []
    assert snapshot["quality_events"] == []


def test_snapshot_uses_backend_responses():
    backend = FakeBackendClient()
    backend.get_responses = {
        "/health": {"status": "ok"},
        "/metrics": {"radiology": {"total_studies": 5}},
        "/studies/history?limit=6": {"items": [{"study_id": "s-1"}]},
        "/quality/events?limit=6": {"items": [{"event_id": "e-1"}]},
    }
    snapshot = DashboardDataService(backend).snapshot()
    assert snapshot["backend_status"] == "ok"
    assert snapshot["metrics"]["radiology"]["total_studies"] == 5
    assert snapshot["recent_studies"] == [{"study_id": "s-1"}]
    assert snapshot["quality_events"] == [{"event_id": "e-1"}]


def test_snapshot_ignores_malformed_responses():
    backend = FakeBackendClient()
    backend.get_responses = {
        "/health": "not-a-dict",
        "/metrics": "broken",
        "/studies/history?limit=6": {"items": "not-a-list"},
        "/quality/events?limit=6": "broken",
    }
    snapshot = DashboardDataService(backend).snapshot()
    assert snapshot["backend_status"] == "no disponible"
    assert snapshot["recent_studies"] == []
