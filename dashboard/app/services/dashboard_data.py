from __future__ import annotations

from typing import Any

from app.services.backend_client import BackendClient


class DashboardDataService:
    """Aggregates backend reads into a single view-model used by the index page."""

    def __init__(self, backend: BackendClient):
        self._backend = backend

    def snapshot(self) -> dict[str, Any]:
        data = self._default()
        health = self._backend.get("/health", {})
        if isinstance(health, dict):
            data["backend_status"] = health.get("status", "no disponible")

        metrics = self._backend.get("/metrics", None)
        if isinstance(metrics, dict):
            data["metrics"] = metrics

        studies = self._backend.get("/studies/history?limit=6", {})
        if isinstance(studies, dict) and isinstance(studies.get("items"), list):
            data["recent_studies"] = studies["items"]

        events = self._backend.get("/quality/events?limit=6", {})
        if isinstance(events, dict) and isinstance(events.get("items"), list):
            data["quality_events"] = events["items"]

        return data

    @staticmethod
    def _default() -> dict[str, Any]:
        return {
            "backend_status": "no disponible",
            "metrics": {
                "radiology": {
                    "total_studies": 0,
                    "class_distribution": {"Sana": 0, "Neumonia": 0, "COVID-19": 0},
                    "warning_count": 0,
                    "average_confidence": 0,
                    "last_study_at": None,
                },
                "triage": {"total_records": 0},
                "pipeline": {"latest_run": None},
                "quality": {"open_events_by_severity": {}},
            },
            "recent_studies": [],
            "quality_events": [],
        }
