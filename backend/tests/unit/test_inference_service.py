from __future__ import annotations

import pytest

from app.services.inference_service import InferenceService
from tests.helpers.images import (
    bright_jpeg_bytes,
    dark_jpeg_bytes,
    jpeg_bytes,
    low_contrast_png_bytes,
)

VALID_CLASSES = {"Sana", "Neumonia", "COVID-19"}


@pytest.fixture
def service() -> InferenceService:
    return InferenceService()


class TestPredictionShape:
    def test_returns_required_keys(self, service):
        result = service.predict(jpeg_bytes())
        assert set(result).issuperset({
            "model_name", "model_version", "model_family",
            "class", "probabilities", "confidence",
            "features", "preprocessing", "quality_flags",
            "explanation", "clinical_note",
        })

    def test_predicted_class_is_known_label(self, service):
        result = service.predict(jpeg_bytes())
        assert result["class"] in VALID_CLASSES

    def test_probabilities_cover_three_classes(self, service):
        result = service.predict(jpeg_bytes())
        assert set(result["probabilities"]) == VALID_CLASSES

    def test_probabilities_sum_to_one(self, service):
        result = service.predict(jpeg_bytes())
        total = sum(result["probabilities"].values())
        assert total == pytest.approx(1.0, abs=0.01)

    def test_confidence_matches_predicted_class(self, service):
        result = service.predict(jpeg_bytes())
        assert result["confidence"] == result["probabilities"][result["class"]]

    def test_features_present(self, service):
        result = service.predict(jpeg_bytes())
        features = result["features"]
        assert "mean_intensity" in features
        assert "contrast" in features
        assert features["input_size_bytes"] > 0


class TestQualityFlags:
    def test_dark_image_flags_exposure(self, service):
        result = service.predict(dark_jpeg_bytes())
        joined = " ".join(result["quality_flags"]).lower()
        assert "oscura" in joined

    def test_bright_image_flags_overexposure(self, service):
        result = service.predict(bright_jpeg_bytes())
        joined = " ".join(result["quality_flags"]).lower()
        assert "clara" in joined

    def test_low_contrast_flag(self, service):
        result = service.predict(low_contrast_png_bytes())
        joined = " ".join(result["quality_flags"]).lower()
        assert "contraste" in joined


class TestDeterminism:
    def test_same_input_same_output(self, service):
        payload = jpeg_bytes(color=(150, 150, 150))
        first = service.predict(payload)
        second = service.predict(payload)
        assert first == second
