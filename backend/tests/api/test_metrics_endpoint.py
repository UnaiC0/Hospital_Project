from __future__ import annotations

from datetime import datetime, timezone

import pytest

pytestmark = pytest.mark.api


def _queue_empty_snapshot(fake_db):
    fake_db.cursor.queue_one({
        "total_studies": 0, "healthy_count": 0, "pneumonia_count": 0,
        "covid_count": 0, "warning_count": 0, "average_confidence": 0, "last_study_at": None,
    })
    fake_db.cursor.queue_one({"total_triage": 0})
    fake_db.cursor.queue_one(None)
    fake_db.cursor.queue_all([])


def test_empty_snapshot(client, fake_db):
    _queue_empty_snapshot(fake_db)
    response = client.get("/metrics")
    assert response.status_code == 200
    body = response.json()
    assert body["radiology"]["total_studies"] == 0
    assert body["triage"]["total_records"] == 0
    assert body["pipeline"]["latest_run"] is None
    assert body["quality"]["open_events_by_severity"] == {}


def test_populated_snapshot(client, fake_db):
    fake_db.cursor.queue_one({
        "total_studies": 10, "healthy_count": 5, "pneumonia_count": 3,
        "covid_count": 2, "warning_count": 1, "average_confidence": 0.75,
        "last_study_at": datetime(2026, 5, 14, tzinfo=timezone.utc),
    })
    fake_db.cursor.queue_one({"total_triage": 4})
    fake_db.cursor.queue_one({
        "id": "p-1",
        "created_at": datetime(2026, 5, 14, tzinfo=timezone.utc),
        "finished_at": datetime(2026, 5, 14, tzinfo=timezone.utc),
        "status": "completed",
        "input_uri": "/data/in.csv",
        "processed_count": 100,
        "rejected_count": 5,
        "report_bucket": "b",
        "report_object_key": "k",
        "metadata": {},
    })
    fake_db.cursor.queue_all([{"severity": "medium", "count": 2}])

    response = client.get("/metrics")
    body = response.json()
    assert body["radiology"]["total_studies"] == 10
    assert body["radiology"]["class_distribution"] == {"Sana": 5, "Neumonia": 3, "COVID-19": 2}
    assert body["pipeline"]["latest_run"]["status"] == "completed"
    assert body["quality"]["open_events_by_severity"] == {"medium": 2}
