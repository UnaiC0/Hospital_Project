from __future__ import annotations

from typing import Any

from app.db.session import DatabaseSession
from app.repositories import metrics_repository, quality_repository
from app.services import triage_model


class MetricsService:
    def __init__(self, db_session: DatabaseSession):
        self._db = db_session

    def platform_snapshot(self) -> dict[str, Any]:
        with self._db.read_cursor() as cursor:
            radiology = metrics_repository.radiology_summary(cursor)
            triage = metrics_repository.triage_count(cursor)
            latest_pipeline = metrics_repository.latest_pipeline_run(cursor)
            open_events = quality_repository.count_open_by_severity(cursor)

        return {
            "radiology": radiology,
            "triage": {"total_records": triage},
            "pipeline": {"latest_run": latest_pipeline},
            "quality": {"open_events_by_severity": open_events},
            "services": {"triage_model": triage_model.model_status()},
        }
