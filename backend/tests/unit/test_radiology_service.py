from __future__ import annotations

from datetime import datetime, timezone

import pytest

from app.services.quality_service import QualityService
from app.services.radiology_service import (
    RadiologyService,
    RadiologyStudyNotFoundError,
)
from tests.helpers.fakes import StubInferenceService
from tests.helpers.images import jpeg_bytes


def build_service(fake_db, fake_storage, inference_response):
    quality = QualityService(fake_db)
    inference = StubInferenceService(inference_response)
    return RadiologyService(
        db_session=fake_db,
        object_storage=fake_storage,
        inference_service=inference,
        quality_service=quality,
    )


def base_response(**overrides):
    response = {
        "model_name": "stub-inference",
        "model_version": "0.0.1",
        "model_family": "stub",
        "class": "Sana",
        "probabilities": {"Sana": 0.8, "Neumonia": 0.15, "COVID-19": 0.05},
        "confidence": 0.8,
        "features": {"mean_intensity": 180.0, "contrast": 40.0, "input_size_bytes": 1024},
        "preprocessing": {"color_space": "grayscale", "resize": [256, 256], "normalization": "stub"},
        "quality_flags": [],
        "explanation": "stub",
        "clinical_note": "stub",
    }
    response.update(overrides)
    return response


class TestPredictAndRegister:
    def test_persists_in_single_transaction(self, fake_db, fake_storage):
        service = build_service(fake_db, fake_storage, base_response())
        result = service.predict_and_register(
            original_filename="scan.jpg",
            content_type="image/jpeg",
            image_bytes=jpeg_bytes(),
            source_object_key=None,
        )
        assert result["study_id"]
        assert fake_db.transaction_count == 1
        # 1 study insert + 0 events (Sana, high confidence, no quality_flags)
        assert len(fake_db.cursor.executed) == 1
        assert result["events"] == []

    def test_uploads_image_when_no_source_key(self, fake_db, fake_storage):
        service = build_service(fake_db, fake_storage, base_response())
        result = service.predict_and_register(
            original_filename="scan.jpg",
            content_type="image/jpeg",
            image_bytes=jpeg_bytes(),
            source_object_key=None,
        )
        assert result["image_object_key"].startswith("uploads/")
        assert result["image_object_key"] in fake_storage.objects

    def test_reuses_existing_object_key(self, fake_db, fake_storage):
        service = build_service(fake_db, fake_storage, base_response())
        result = service.predict_and_register(
            original_filename="scan.jpg",
            content_type="image/jpeg",
            image_bytes=jpeg_bytes(),
            source_object_key="uploads/existing.jpg",
        )
        assert result["image_object_key"] == "uploads/existing.jpg"

    def test_report_stored_as_json(self, fake_db, fake_storage):
        service = build_service(fake_db, fake_storage, base_response())
        result = service.predict_and_register(
            original_filename="scan.jpg",
            content_type="image/jpeg",
            image_bytes=jpeg_bytes(),
            source_object_key=None,
        )
        document, content_type = fake_storage.objects[result["report_object_key"]]
        assert content_type == "application/json"
        assert document["study_id"] == result["study_id"]
        assert document["image"]["checksum_sha256"]
        assert document["prediction"]["class"] == "Sana"

    def test_quality_status_accepted_without_flags(self, fake_db, fake_storage):
        service = build_service(fake_db, fake_storage, base_response())
        result = service.predict_and_register(
            original_filename="scan.jpg",
            content_type="image/jpeg",
            image_bytes=jpeg_bytes(),
            source_object_key=None,
        )
        assert result["quality_status"] == "accepted"

    def test_quality_status_warning_with_flags(self, fake_db, fake_storage):
        response = base_response(quality_flags=["dark"])
        service = build_service(fake_db, fake_storage, response)
        result = service.predict_and_register(
            original_filename="scan.jpg",
            content_type="image/jpeg",
            image_bytes=jpeg_bytes(),
            source_object_key=None,
        )
        assert result["quality_status"] == "warning"


class TestQualityEvents:
    def test_covid_emits_clinical_alert(self, fake_db, fake_storage):
        response = base_response(
            **{"class": "COVID-19", "probabilities": {"Sana": 0.1, "Neumonia": 0.1, "COVID-19": 0.8}, "confidence": 0.8}
        )
        service = build_service(fake_db, fake_storage, response)
        result = service.predict_and_register(
            original_filename="scan.jpg",
            content_type="image/jpeg",
            image_bytes=jpeg_bytes(),
            source_object_key=None,
        )
        types = [event["event_type"] for event in result["events"]]
        assert "clinical_alert" in types

    def test_low_confidence_emits_event(self, fake_db, fake_storage):
        response = base_response(confidence=0.3)
        service = build_service(fake_db, fake_storage, response)
        result = service.predict_and_register(
            original_filename="scan.jpg",
            content_type="image/jpeg",
            image_bytes=jpeg_bytes(),
            source_object_key=None,
        )
        types = [event["event_type"] for event in result["events"]]
        assert "low_model_confidence" in types

    def test_quality_flags_emit_event(self, fake_db, fake_storage):
        response = base_response(quality_flags=["dark", "low contrast"])
        service = build_service(fake_db, fake_storage, response)
        result = service.predict_and_register(
            original_filename="scan.jpg",
            content_type="image/jpeg",
            image_bytes=jpeg_bytes(),
            source_object_key=None,
        )
        types = [event["event_type"] for event in result["events"]]
        assert "image_quality" in types

    def test_all_three_events_when_all_conditions_met(self, fake_db, fake_storage):
        response = base_response(
            **{
                "class": "COVID-19",
                "confidence": 0.3,
                "quality_flags": ["dark"],
            }
        )
        service = build_service(fake_db, fake_storage, response)
        result = service.predict_and_register(
            original_filename="scan.jpg",
            content_type="image/jpeg",
            image_bytes=jpeg_bytes(),
            source_object_key=None,
        )
        types = {event["event_type"] for event in result["events"]}
        assert types == {"clinical_alert", "low_model_confidence", "image_quality"}
        # All four inserts (study + 3 events) live in ONE transaction → ACID
        assert fake_db.transaction_count == 1
        assert len(fake_db.cursor.executed) == 4


class TestQueries:
    def test_list_history(self, fake_db, fake_storage):
        service = build_service(fake_db, fake_storage, base_response())
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
                "probabilities": {"Sana": 1.0},
                "model_name": "m",
                "model_version": "v",
                "confidence": 0.9,
                "quality_status": "accepted",
                "quality_messages": [],
                "report_bucket": "b",
                "report_object_key": "rk",
            }
        ])
        items = service.list_history(5)
        assert len(items) == 1
        assert items[0]["study_id"] == "s-1"

    def test_get_missing_raises(self, fake_db, fake_storage):
        service = build_service(fake_db, fake_storage, base_response())
        fake_db.cursor.queue_one(None)
        with pytest.raises(RadiologyStudyNotFoundError):
            service.get("nope")

    def test_get_report_loads_from_storage(self, fake_db, fake_storage):
        service = build_service(fake_db, fake_storage, base_response())
        fake_storage.objects["radiology-reports/s-1.json"] = ({"k": "v"}, "application/json")
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
            "probabilities": {"Sana": 1.0},
            "model_name": "m",
            "model_version": "v",
            "confidence": 0.9,
            "quality_status": "accepted",
            "quality_messages": [],
            "model_response": {},
            "report_bucket": "b",
            "report_object_key": "radiology-reports/s-1.json",
        })
        assert service.get_report("s-1") == {"k": "v"}
