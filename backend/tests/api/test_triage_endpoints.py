from __future__ import annotations

from datetime import datetime, timezone

import pytest

pytestmark = pytest.mark.api


class TestTriageCreate:
    def test_minimal_payload_returns_200(self, client):
        response = client.post("/triage", json={"patient_name": "Test"})
        assert response.status_code == 200
        body = response.json()
        assert body["status"] == "accepted"
        assert body["triage_id"]
        assert body["patient_id"]
        assert body["patient_name"] == "Test"
        assert body["patient_assessment"]["risk_level"] == "low"

    def test_critical_payload_returns_critical_risk(self, client):
        response = client.post(
            "/triage",
            json={
                "patient_name": "Test",
                "symptoms": ["chest pain"],
                "vitals": {"heart_rate": 130, "oxygen_saturation": 80, "systolic_bp": 80},
            },
        )
        assert response.status_code == 200
        body = response.json()
        assert body["patient_assessment"]["risk_level"] == "critical"
        assert body["patient_assessment"]["recommended_priority"] == "immediate"

    def test_storage_info_present(self, client):
        response = client.post("/triage", json={"patient_name": "Test"})
        storage = response.json()["storage"]
        assert "postgres_database" in storage
        assert "minio_bucket" in storage
        assert storage["minio_object_key"].startswith("triage-reports/")

    def test_invalid_payload_returns_422(self, client):
        response = client.post("/triage", json={"symptoms": "not-a-list"})
        assert response.status_code == 422


class TestTriageHistory:
    def test_default_limit(self, client, fake_db):
        fake_db.cursor.queue_all([])
        response = client.get("/triage/history")
        assert response.status_code == 200
        assert response.json() == {"count": 0, "items": []}

    def test_returns_mapped_items(self, client, fake_db):
        fake_db.cursor.queue_all([
            {
                "id": "t-1",
                "patient_id": "PAC-00000001",
                "patient_name": "Test Patient",
                "created_at": datetime(2026, 1, 1, tzinfo=timezone.utc),
                "risk_level": "low",
                "recommended_priority": "standard",
                "score": 0,
                "confidence": 0.65,
                "report_bucket": "b",
                "report_object_key": "k",
            }
        ])
        response = client.get("/triage/history?limit=5")
        body = response.json()
        assert body["count"] == 1
        assert body["items"][0]["triage_id"] == "t-1"

    def test_limit_bounds_validated(self, client):
        assert client.get("/triage/history?limit=0").status_code == 422
        assert client.get("/triage/history?limit=101").status_code == 422


class TestTriageDetail:
    def test_returns_record(self, client, fake_db):
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
        response = client.get("/triage/t-1")
        assert response.status_code == 200
        assert response.json()["triage_id"] == "t-1"

    def test_not_found_returns_404(self, client, fake_db):
        fake_db.cursor.queue_one(None)
        response = client.get("/triage/nope")
        assert response.status_code == 404
        assert response.json()["detail"] == "Triage record not found"


class TestTriageReport:
    def test_returns_report_document(self, client, fake_db, fake_storage):
        fake_storage.objects["triage-reports/t-1.json"] = ({"hello": "world"}, "application/json")
        fake_db.cursor.queue_one({
            "id": "t-1",
            "patient_id": "PAC-00000001",
            "patient_name": "Test Patient",
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
        response = client.get("/triage/t-1/report")
        assert response.status_code == 200
        assert response.json() == {"hello": "world"}

    def test_missing_returns_404(self, client, fake_db):
        fake_db.cursor.queue_one(None)
        response = client.get("/triage/nope/report")
        assert response.status_code == 404
