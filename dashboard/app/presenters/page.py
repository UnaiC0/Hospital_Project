from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from app.core.config import ObjectStorageSettings
from app.presenters.prediction import (
    build_result_context,
    normalize_probabilities,
)
from app.services.dashboard_data import DashboardDataService
from app.triage.catalog import TRIAGE_SYMPTOMS, TRIAGE_VITAL_FIELDS
from app.triage.parser import empty_triage_form_values


@dataclass(frozen=True)
class PageInputs:
    error: str | None = None
    success: str | None = None
    image_preview: str | None = None
    prediction_class: str | None = None
    probabilities: list[tuple[str, float]] | None = None
    object_key: str | None = None
    uploaded_filename: str | None = None
    uploaded_size: str | None = None
    study_id: str | None = None
    report_object_key: str | None = None
    triage_result: dict | None = None
    triage_form_values: dict | None = None
    triage_error: str | None = None
    triage_success: str | None = None
    default_tab: str = "overview"


class PagePresenter:
    """Builds the template context for the main page view. Decouples blueprints
    from string formatting and from how dashboard data is fetched."""

    def __init__(self, storage_settings: ObjectStorageSettings, data_service: DashboardDataService):
        self._storage_settings = storage_settings
        self._data_service = data_service

    def build_context(self, inputs: PageInputs) -> dict[str, Any]:
        dashboard = self._data_service.snapshot()
        has_image = bool(inputs.image_preview)
        has_result = bool(inputs.prediction_class)
        result = build_result_context(inputs.prediction_class)
        file_status = self._file_status(inputs, has_result)

        return {
            "error": inputs.error,
            "success": inputs.success,
            "image_preview": inputs.image_preview,
            "prediction_class": inputs.prediction_class,
            "probability_rows": normalize_probabilities(inputs.probabilities),
            "object_key": inputs.object_key,
            "study_id": inputs.study_id,
            "report_object_key": inputs.report_object_key,
            "uploaded_filename": inputs.uploaded_filename or "Ningun archivo cargado",
            "uploaded_size": inputs.uploaded_size,
            "file_status": file_status,
            "has_image": has_image,
            "has_result": has_result,
            "result": result,
            "minio_bucket_name": self._storage_settings.bucket_name,
            "minio_console_url": self._storage_settings.console_url,
            "minio_endpoint": self._storage_settings.endpoint,
            "backend_status": dashboard["backend_status"],
            "dashboard_metrics": dashboard["metrics"],
            "recent_studies": dashboard["recent_studies"],
            "quality_events": dashboard["quality_events"],
            "recent_triages": dashboard.get("recent_triages", []),
            "triage_model_status": dashboard.get("triage_model", {"loaded": False, "model_name": None}),
            "triage_result": inputs.triage_result,
            "triage_form_values": inputs.triage_form_values or empty_triage_form_values(),
            "triage_error": inputs.triage_error,
            "triage_success": inputs.triage_success,
            "triage_symptoms_catalog": TRIAGE_SYMPTOMS,
            "triage_vital_fields": TRIAGE_VITAL_FIELDS,
            "has_triage": bool(inputs.triage_result),
            "default_tab": (
                "triage" if inputs.triage_result
                else "report" if has_result
                else inputs.default_tab
            ),
        }

    @staticmethod
    def _file_status(inputs: PageInputs, has_result: bool) -> str:
        if inputs.uploaded_filename and inputs.uploaded_size and has_result:
            return f"{inputs.uploaded_size} - Analisis completado"
        if inputs.uploaded_filename and inputs.uploaded_size:
            return f"{inputs.uploaded_size} - Listo para procesar"
        return "Seleccione una radiografia JPG, JPEG o PNG"
