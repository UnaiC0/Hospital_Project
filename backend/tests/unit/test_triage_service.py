from __future__ import annotations

from datetime import datetime, timezone

import pytest

from app.schemas.triage import TriageRequest
from app.services.triage_service import TriageNotFoundError, TriageService
from tests.helpers.fakes import FakeDatabaseSession, FakeObjectStorage


@pytest.fixture
def service(fake_db: FakeDatabaseSession, fake_storage: FakeObjectStorage) -> TriageService:
    return TriageService(fake_db, fake_storage)


class TestRegister:
    def test_inserts_db_row_and_uploads_report(self, service, fake_db, fake_storage):
        request = TriageRequest(patient_name="Test", symptoms=["fever"])
        assessment = service.assess(request)

        result = service.register(request, assessment)

        assert result["triage_id"]
        assert result["patient_id"]
        assert result["patient_name"] == "Test"
        assert result["report_bucket"] == fake_storage.bucket
        assert result["report_object_key"].startswith("triage-reports/")
        assert fake_storage.ensure_bucket_calls >= 1
        assert result["report_object_key"] in fake_storage.objects
        assert fake_db.transaction_count == 1
        assert len(fake_db.cursor.executed) == 1

    def test_report_document_contains_request_and_assessment(self, service, fake_storage):
        request = TriageRequest(patient_name="Test", symptoms=["chest pain"], notes="patient anxious")
        assessment = service.assess(request)
        result = service.register(request, assessment)

        document, content_type = fake_storage.objects[result["report_object_key"]]
        assert content_type == "application/json"
        assert document["request"]["notes"] == "patient anxious"
        assert document["assessment"] == assessment


class TestListHistory:
    def test_maps_rows(self, service, fake_db):
        fake_db.cursor.queue_all([
            {
                "id": "t-1",
                "patient_id": "PAC-00000001",
                "patient_name": "Test Patient",
                "created_at": datetime(2026, 1, 1, tzinfo=timezone.utc),
                "risk_level": "low",
                "recommended_priority": "standard",
                "score": 5,
                "confidence": 0.7,
                "report_bucket": "b",
                "report_object_key": "k",
            }
        ])
        items = service.list_history(10)
        assert items == [{
            "triage_id": "t-1",
            "patient_id": "PAC-00000001",
            "patient_name": "Test Patient",
            "created_at": "2026-01-01T00:00:00+00:00",
            "risk_level": "low",
            "recommended_priority": "standard",
            "score": 5,
            "confidence": 0.7,
            "report_bucket": "b",
            "report_object_key": "k",
        }]


class TestGet:
    def test_returns_record(self, service, fake_db):
        fake_db.cursor.queue_one({
            "id": "t-1",
            "patient_id": "PAC-00000001",
            "patient_name": "Test Patient",
            "created_at": datetime(2026, 1, 1, tzinfo=timezone.utc),
            "request_payload": {"symptoms": []},
            "model_response": {"risk_level": "low"},
            "risk_level": "low",
            "recommended_priority": "standard",
            "score": 0,
            "confidence": 0.65,
            "report_bucket": "b",
            "report_object_key": "k",
        })
        record = service.get("t-1")
        assert record["triage_id"] == "t-1"
        assert record["assessment"] == {"risk_level": "low"}

    def test_missing_raises(self, service, fake_db):
        fake_db.cursor.queue_one(None)
        with pytest.raises(TriageNotFoundError):
            service.get("nope")


class TestGetReport:
    def test_loads_report_from_storage(self, service, fake_db, fake_storage):
        fake_storage.objects["triage-reports/t-1.json"] = ({"hello": "world"}, "application/json")
        fake_db.cursor.queue_one({
            "id": "t-1",
            "created_at": datetime(2026, 1, 1, tzinfo=timezone.utc),
            "request_payload": {},
            "model_response": {},
            "risk_level": "low",
            "recommended_priority": "standard",
            "score": 0,
            "confidence": 0.65,
            "report_bucket": "b",
            "report_object_key": "triage-reports/t-1.json",
        })
        assert service.get_report("t-1") == {"hello": "world"}

    def test_missing_raises(self, service, fake_db):
        fake_db.cursor.queue_one(None)
        with pytest.raises(TriageNotFoundError):
            service.get_report("nope")
