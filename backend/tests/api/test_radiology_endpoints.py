from __future__ import annotations

from datetime import datetime, timezone

import pytest

from tests.helpers.images import jpeg_bytes, png_bytes

pytestmark = pytest.mark.api


class TestPredict:
    def test_valid_jpeg_returns_200(self, client):
        response = client.post(
            "/predict",
            files={"file": ("scan.jpg", jpeg_bytes(), "image/jpeg")},
        )
        assert response.status_code == 200
        body = response.json()
        assert body["study_id"]
        assert body["class"] in {"Sana", "Neumonia", "COVID-19"}
        assert body["quality_status"] in {"accepted", "warning"}
        assert "storage" in body
        assert "events" in body

    def test_valid_png_returns_200(self, client):
        response = client.post(
            "/predict",
            files={"file": ("scan.png", png_bytes(), "image/png")},
        )
        assert response.status_code == 200

    def test_missing_file_returns_422(self, client):
        response = client.post("/predict")
        assert response.status_code == 422

    def test_unsupported_extension_returns_400(self, client):
        response = client.post(
            "/predict",
            files={"file": ("scan.gif", jpeg_bytes(), "image/gif")},
        )
        assert response.status_code == 400

    def test_extension_mime_mismatch_returns_400(self, client):
        response = client.post(
            "/predict",
            files={"file": ("scan.jpg", png_bytes(), "image/jpeg")},
        )
        assert response.status_code == 400

    def test_empty_file_returns_400(self, client):
        response = client.post(
            "/predict",
            files={"file": ("scan.jpg", b"", "image/jpeg")},
        )
        assert response.status_code == 400

    def test_non_image_bytes_returns_400(self, client):
        response = client.post(
            "/predict",
            files={"file": ("scan.jpg", b"not-an-image-actually", "image/jpeg")},
        )
        assert response.status_code == 400

    def test_with_source_object_key(self, client):
        response = client.post(
            "/predict",
            files={"file": ("scan.jpg", jpeg_bytes(), "image/jpeg")},
            data={"source_object_key": "uploads/preexisting.jpg"},
        )
        assert response.status_code == 200
        assert response.json()["storage"]["image_object_key"] == "uploads/preexisting.jpg"


class TestStudiesHistory:
    def test_empty_history(self, client, fake_db):
        fake_db.cursor.queue_all([])
        response = client.get("/studies/history")
        assert response.status_code == 200
        assert response.json() == {"count": 0, "items": []}

    def test_returns_mapped_items(self, client, fake_db):
        fake_db.cursor.queue_all([
            {
                "id": "s-1",
                "created_at": datetime(2026, 1, 1, tzinfo=timezone.utc),
                "original_filename": "a.jpg",
                "content_type": "image/jpeg",
                "file_size_bytes": 100,
                "image_bucket": "b",
                "image_object_key": "k",
                "prediction_class": "Sana",
                "probabilities": {"Sana": 1.0, "Neumonia": 0, "COVID-19": 0},
                "model_name": "m",
                "model_version": "v",
                "confidence": 0.9,
                "quality_status": "accepted",
                "quality_messages": [],
                "report_bucket": "b",
                "report_object_key": "rk",
            }
        ])
        response = client.get("/studies/history?limit=3")
        body = response.json()
        assert body["count"] == 1
        assert body["items"][0]["study_id"] == "s-1"

    def test_limit_validation(self, client):
        assert client.get("/studies/history?limit=0").status_code == 422
        assert client.get("/studies/history?limit=999").status_code == 422


class TestStudyDetail:
    def test_returns_record(self, client, fake_db):
        fake_db.cursor.queue_one({
            "id": "s-1",
            "created_at": datetime(2026, 1, 1, tzinfo=timezone.utc),
            "original_filename": "a.jpg",
            "content_type": "image/jpeg",
            "file_size_bytes": 100,
            "checksum_sha256": "x",
            "image_bucket": "b",
            "image_object_key": "k",
            "prediction_class": "Sana",
            "probabilities": {"Sana": 1.0, "Neumonia": 0, "COVID-19": 0},
            "model_name": "m",
            "model_version": "v",
            "confidence": 0.9,
            "quality_status": "accepted",
            "quality_messages": [],
            "model_response": {},
            "report_bucket": "b",
            "report_object_key": "rk",
        })
        response = client.get("/studies/s-1")
        assert response.status_code == 200
        assert response.json()["study_id"] == "s-1"

    def test_not_found_returns_404(self, client, fake_db):
        fake_db.cursor.queue_one(None)
        response = client.get("/studies/nope")
        assert response.status_code == 404


class TestStudyReport:
    def test_returns_report(self, client, fake_db, fake_storage):
        fake_storage.objects["radiology-reports/s-1.json"] = ({"x": 1}, "application/json")
        fake_db.cursor.queue_one({
            "id": "s-1",
            "created_at": datetime(2026, 1, 1, tzinfo=timezone.utc),
            "original_filename": "a.jpg",
            "content_type": "image/jpeg",
            "file_size_bytes": 100,
            "checksum_sha256": "x",
            "image_bucket": "b",
            "image_object_key": "k",
            "prediction_class": "Sana",
            "probabilities": {"Sana": 1.0, "Neumonia": 0, "COVID-19": 0},
            "model_name": "m",
            "model_version": "v",
            "confidence": 0.9,
            "quality_status": "accepted",
            "quality_messages": [],
            "model_response": {},
            "report_bucket": "b",
            "report_object_key": "radiology-reports/s-1.json",
        })
        response = client.get("/studies/s-1/report")
        assert response.status_code == 200
        assert response.json() == {"x": 1}

    def test_missing_returns_404(self, client, fake_db):
        fake_db.cursor.queue_one(None)
        response = client.get("/studies/nope/report")
        assert response.status_code == 404
