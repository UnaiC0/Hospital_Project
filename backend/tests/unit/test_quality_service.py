from __future__ import annotations

from datetime import datetime, timezone

import pytest

from app.services.quality_service import QualityEventNotFoundError, QualityService


@pytest.fixture
def service(fake_db) -> QualityService:
    return QualityService(fake_db)


class TestRecord:
    def test_inserts_using_caller_cursor(self, service, fake_db):
        event = service.record(
            fake_db.cursor,
            source="radiology",
            severity="high",
            event_type="clinical_alert",
            message="test",
            metadata={"k": "v"},
        )
        assert event["event_id"]
        assert event["source"] == "radiology"
        assert event["metadata"] == {"k": "v"}
        # one execute on the cursor, transaction owned by caller
        assert len(fake_db.cursor.executed) == 1
        assert fake_db.transaction_count == 0

    def test_default_metadata_is_empty_dict(self, service, fake_db):
        event = service.record(
            fake_db.cursor,
            source="x",
            severity="low",
            event_type="t",
            message="m",
        )
        assert event["metadata"] == {}


class TestResolve:
    def test_marks_event_resolved(self, service, fake_db):
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
        updated = service.resolve("e-1")
        assert updated["event_id"] == "e-1"
        assert updated["resolved"] is True
        # the update must run inside an ACID transaction
        assert fake_db.transaction_count == 1

    def test_missing_event_raises(self, service, fake_db):
        fake_db.cursor.queue_one(None)
        with pytest.raises(QualityEventNotFoundError):
            service.resolve("missing")


class TestListRecent:
    def test_maps_rows(self, service, fake_db):
        fake_db.cursor.queue_all([
            {
                "id": "e-1",
                "created_at": datetime(2026, 1, 1, tzinfo=timezone.utc),
                "source": "radiology",
                "severity": "high",
                "event_type": "clinical_alert",
                "message": "msg",
                "metadata": {"k": "v"},
                "resolved": False,
            }
        ])
        events = service.list_recent(10)
        assert events == [{
            "event_id": "e-1",
            "created_at": "2026-01-01T00:00:00+00:00",
            "source": "radiology",
            "severity": "high",
            "event_type": "clinical_alert",
            "message": "msg",
            "metadata": {"k": "v"},
            "resolved": False,
        }]
