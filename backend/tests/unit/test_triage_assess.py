from __future__ import annotations

import pytest

from app.schemas.triage import TriageRequest
from app.services.quality_service import QualityService
from app.services.triage_service import TriageService
from tests.helpers.fakes import FakeDatabaseSession, FakeObjectStorage


@pytest.fixture
def service() -> TriageService:
    db = FakeDatabaseSession()
    return TriageService(
        db_session=db,
        object_storage=FakeObjectStorage(),
        quality_service=QualityService(db),
    )


class TestRiskBuckets:
    def test_empty_payload_is_low_risk(self, service):
        assessment = service.assess(TriageRequest())
        assert assessment["risk_level"] == "low"
        assert assessment["recommended_priority"] == "standard"
        assert assessment["score"] == 0

    def test_chest_pain_escalates(self, service):
        assessment = service.assess(TriageRequest(symptoms=["chest pain"]))
        assert assessment["score"] >= 35
        assert assessment["risk_level"] in {"medium", "high", "critical"}

    def test_low_oxygen_adds_25(self, service):
        baseline = service.assess(TriageRequest())["score"]
        with_low_oxygen = service.assess(
            TriageRequest(vitals={"oxygen_saturation": 88})
        )["score"]
        assert with_low_oxygen - baseline == 25

    def test_low_blood_pressure_adds_20(self, service):
        with_low_bp = service.assess(TriageRequest(vitals={"systolic_bp": 80}))["score"]
        assert with_low_bp == 20

    def test_high_heart_rate_adds_15(self, service):
        with_hr = service.assess(TriageRequest(vitals={"heart_rate": 130}))["score"]
        assert with_hr == 15

    def test_score_caps_at_100(self, service):
        assessment = service.assess(
            TriageRequest(
                symptoms=[
                    "chest pain",
                    "shortness of breath",
                    "loss of consciousness",
                    "fever",
                    "cough",
                    "vomiting",
                ],
                vitals={"heart_rate": 140, "oxygen_saturation": 80, "systolic_bp": 70},
            )
        )
        assert assessment["score"] == 100
        assert assessment["risk_level"] == "critical"

    def test_symptom_score_caps_at_40(self, service):
        many = service.assess(
            TriageRequest(symptoms=["fever"] * 20)
        )["score"]
        assert many == 8  # de-duplicated to {"fever"} → 8

    def test_critical_bucket(self, service):
        assessment = service.assess(
            TriageRequest(
                symptoms=["chest pain"],
                vitals={"heart_rate": 130, "oxygen_saturation": 80},
            )
        )
        assert assessment["risk_level"] == "critical"
        assert assessment["recommended_priority"] == "immediate"

    def test_medium_bucket(self, service):
        # 4 symptoms (32 pts) + tachycardia (15) = 47 → medium (25..49)
        assessment = service.assess(
            TriageRequest(
                symptoms=["fever", "cough", "fatigue", "headache"],
                vitals={"heart_rate": 130},
            )
        )
        assert assessment["risk_level"] == "medium"
        assert assessment["recommended_priority"] == "priority"

    def test_high_bucket(self, service):
        # Symptoms cap 40 + tachycardia 15 = 55 → high
        assessment = service.assess(
            TriageRequest(
                symptoms=["fever", "cough", "fatigue", "headache", "dizziness"],
                vitals={"heart_rate": 130},
            )
        )
        assert assessment["risk_level"] == "high"
        assert assessment["recommended_priority"] == "urgent"


class TestVitalsCoercion:
    def test_non_numeric_vitals_fall_back_to_defaults(self, service):
        assessment = service.assess(
            TriageRequest(vitals={"heart_rate": "abc", "oxygen_saturation": None})
        )
        assert assessment["score"] == 0

    def test_empty_string_symptoms_are_filtered(self, service):
        assessment = service.assess(TriageRequest(symptoms=["", ""]))
        assert assessment["score"] == 0


class TestConfidence:
    def test_confidence_grows_with_score(self, service):
        low = service.assess(TriageRequest())
        high = service.assess(
            TriageRequest(symptoms=["chest pain"], vitals={"oxygen_saturation": 80})
        )
        assert high["confidence"] > low["confidence"]
