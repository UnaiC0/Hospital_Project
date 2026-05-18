from __future__ import annotations

from datetime import datetime, timezone

import pytest

pytestmark = pytest.mark.api


def test_empty_events(client, fake_db):
    fake_db.cursor.queue_all([])
    response = client.get("/quality/events")
    assert response.status_code == 200
    assert response.json() == {"count": 0, "items": []}


def test_returns_mapped_items(client, fake_db):
    fake_db.cursor.queue_all([
        {
            "id": "e-1",
            "created_at": datetime(2026, 1, 1, tzinfo=timezone.utc),
            "source": "radiology",
            "severity": "high",
            "event_type": "clinical_alert",
            "message": "msg",
            "metadata": {"x": "y"},
            "resolved": False,
        }
    ])
    response = client.get("/quality/events?limit=5")
    body = response.json()
    assert body["count"] == 1
    item = body["items"][0]
    assert item["event_id"] == "e-1"
    assert item["severity"] == "high"


def test_limit_validation(client):
    assert client.get("/quality/events?limit=0").status_code == 422
    assert client.get("/quality/events?limit=500").status_code == 422


class TestResolveEndpoint:
    def test_resolve_marks_event(self, client, fake_db):
        fake_db.cursor.queue_one({
            "id": "e-1",
            "created_at": datetime(2026, 1, 1, tzinfo=timezone.utc),
            "source": "radiology",
            "severity": "high",
            "event_type": "clinical_alert",
            "message": "msg",
            "metadata": {},
            "resolved": True,
        })
        response = client.patch("/quality/events/e-1/resolve")
        assert response.status_code == 200
        body = response.json()
        assert body["event_id"] == "e-1"
        assert body["resolved"] is True

    def test_missing_event_returns_404(self, client, fake_db):
        fake_db.cursor.queue_one(None)
        response = client.patch("/quality/events/missing/resolve")
        assert response.status_code == 404
        assert response.json()["detail"] == "Quality event not found"
