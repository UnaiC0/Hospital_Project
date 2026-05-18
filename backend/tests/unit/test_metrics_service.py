from __future__ import annotations

from datetime import datetime, timezone

import pytest

from app.services.metrics_service import MetricsService


@pytest.fixture
def service(fake_db) -> MetricsService:
    return MetricsService(fake_db)


class TestPlatformSnapshot:
    def test_composes_all_sections(self, service, fake_db):
        fake_db.cursor.queue_one({  # radiology summary
            "total_studies": 12,
            "healthy_count": 6,
            "pneumonia_count": 4,
            "covid_count": 2,
            "warning_count": 3,
            "average_confidence": 0.83,
            "last_study_at": datetime(2026, 5, 14, 10, tzinfo=timezone.utc),
        })
        fake_db.cursor.queue_one({"total_triage": 7})
        fake_db.cursor.queue_one({  # latest pipeline run
            "id": "p-1",
            "created_at": datetime(2026, 5, 14, tzinfo=timezone.utc),
            "finished_at": datetime(2026, 5, 14, tzinfo=timezone.utc),
            "status": "completed",
            "input_uri": "/data/in.csv",
            "processed_count": 10,
            "rejected_count": 2,
            "report_bucket": "b",
            "report_object_key": "k",
            "metadata": {"x": 1},
        })
        fake_db.cursor.queue_all([
            {"severity": "high", "count": 1},
            {"severity": "medium", "count": 3},
        ])

        snapshot = service.platform_snapshot()

        assert snapshot["radiology"]["total_studies"] == 12
        assert snapshot["radiology"]["class_distribution"] == {"Sana": 6, "Neumonia": 4, "COVID-19": 2}
        assert snapshot["radiology"]["average_confidence"] == 0.83
        assert snapshot["triage"] == {"total_records": 7}
        assert snapshot["pipeline"]["latest_run"]["status"] == "completed"
        assert snapshot["quality"]["open_events_by_severity"] == {"high": 1, "medium": 3}

    def test_no_pipeline_run_returns_none(self, service, fake_db):
        fake_db.cursor.queue_one({
            "total_studies": 0, "healthy_count": 0, "pneumonia_count": 0,
            "covid_count": 0, "warning_count": 0, "average_confidence": 0, "last_study_at": None,
        })
        fake_db.cursor.queue_one({"total_triage": 0})
        fake_db.cursor.queue_one(None)
        fake_db.cursor.queue_all([])
        snapshot = service.platform_snapshot()
        assert snapshot["pipeline"]["latest_run"] is None
        assert snapshot["radiology"]["last_study_at"] is None
