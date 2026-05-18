from __future__ import annotations

import pytest

from app.presenters.prediction import (
    build_image_preview,
    build_result_context,
    format_file_size,
    normalize_backend_prediction,
    normalize_probabilities,
)


def test_normalize_probabilities_returns_three_rows_in_display_order():
    rows = normalize_probabilities([("COVID-19", 0.1), ("Sana", 0.8), ("Neumonia", 0.1)])
    assert [r["label"] for r in rows] == ["Sana", "Neumonia", "COVID-19"]
    assert rows[0]["percent"] == 80.0


def test_normalize_probabilities_clamps_to_valid_range():
    rows = normalize_probabilities([("Sana", 1.5), ("Neumonia", -0.2), ("COVID-19", 0.5)])
    assert rows[0]["value"] == 1.0
    assert rows[1]["value"] == 0.0


def test_normalize_probabilities_none_returns_zeros():
    rows = normalize_probabilities(None)
    assert all(r["value"] == 0.0 for r in rows)


def test_build_result_context_known_class():
    ctx = build_result_context("Sana")
    assert ctx["state"] == "healthy"
    assert ctx["title"] == "Sana"


def test_build_result_context_pending_when_unknown():
    ctx = build_result_context(None)
    assert ctx["state"] == "pending"


def test_build_image_preview_returns_data_url():
    url = build_image_preview(b"abc", "image/jpeg")
    assert url.startswith("data:image/jpeg;base64,")


def test_format_file_size_megabytes():
    assert format_file_size(b"\x00" * (1024 * 1024)) == "1.0 MB"


class TestNormalizeBackendPrediction:
    def test_well_formed(self):
        result = normalize_backend_prediction({
            "class": "Sana",
            "probabilities": {"Sana": 0.7, "Neumonia": 0.2, "COVID-19": 0.1},
            "study_id": "s-1",
            "storage": {"report_object_key": "rk"},
        })
        assert result["class"] == "Sana"
        assert result["probabilities"][0] == ("Sana", 0.7)
        assert result["study_id"] == "s-1"

    def test_missing_class_raises(self):
        with pytest.raises(ValueError):
            normalize_backend_prediction({"probabilities": {}})

    def test_non_numeric_probability_raises(self):
        with pytest.raises(ValueError):
            normalize_backend_prediction({"class": "Sana", "probabilities": {"Sana": "abc"}})
