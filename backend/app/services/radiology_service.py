from __future__ import annotations

import hashlib
import os
from datetime import datetime, timezone
from typing import Any
from uuid import uuid4

from app.db.session import DatabaseSession
from app.repositories import radiology_repository
from app.services.inference_service import InferenceService
from app.services.quality_service import QualityService
from app.storage.object_storage import ObjectStorage


class RadiologyStudyNotFoundError(LookupError):
    pass


class RadiologyService:
    """Orchestrates a complete radiology study: prediction, persistence, and
    quality events. All DB writes happen inside one transaction to guarantee
    atomicity (study and its derived quality events commit together or not at all).
    """

    LOW_CONFIDENCE_THRESHOLD = 0.55
    CRITICAL_PREDICTION_CLASS = "COVID-19"

    def __init__(
        self,
        db_session: DatabaseSession,
        object_storage: ObjectStorage,
        inference_service: InferenceService,
        quality_service: QualityService,
    ):
        self._db = db_session
        self._storage = object_storage
        self._inference = inference_service
        self._quality = quality_service

    def predict_and_register(
        self,
        *,
        original_filename: str,
        content_type: str,
        image_bytes: bytes,
        source_object_key: str | None,
    ) -> dict[str, Any]:
        prediction = self._inference.predict(image_bytes)

        study_id = str(uuid4())
        created_at = datetime.now(timezone.utc)
        checksum_sha256 = hashlib.sha256(image_bytes).hexdigest()
        quality_messages = self._safe_list(prediction.get("quality_flags"))
        quality_status = "warning" if quality_messages else "accepted"
        probabilities = prediction.get("probabilities", {})
        prediction_class = str(prediction.get("class", "unknown"))
        confidence = float(prediction.get("confidence", 0.0) or 0.0)
        model_name = str(prediction.get("model_name", "unknown"))
        model_version = str(prediction.get("model_version", "unknown"))

        self._storage.ensure_bucket()
        image_object_key = self._persist_image(
            source_object_key=source_object_key,
            study_id=study_id,
            original_filename=original_filename,
            content_type=content_type,
            image_bytes=image_bytes,
        )

        report_object_key = f"radiology-reports/{study_id}.json"
        report_document = self._build_report(
            study_id=study_id,
            created_at=created_at,
            original_filename=original_filename,
            content_type=content_type,
            image_bytes=image_bytes,
            checksum_sha256=checksum_sha256,
            image_object_key=image_object_key,
            prediction=prediction,
            prediction_class=prediction_class,
            confidence=confidence,
            quality_status=quality_status,
            quality_messages=quality_messages,
            report_object_key=report_object_key,
        )
        self._storage.put_json(report_object_key, report_document)

        with self._db.transaction() as cursor:
            radiology_repository.insert(
                cursor,
                study_id=study_id,
                created_at=created_at,
                original_filename=original_filename,
                content_type=content_type,
                file_size_bytes=len(image_bytes),
                checksum_sha256=checksum_sha256,
                image_bucket=self._storage.bucket,
                image_object_key=image_object_key,
                prediction_class=prediction_class,
                probabilities=probabilities,
                model_name=model_name,
                model_version=model_version,
                confidence=confidence,
                quality_status=quality_status,
                quality_messages=quality_messages,
                model_response=prediction,
                report_bucket=self._storage.bucket,
                report_object_key=report_object_key,
            )
            events = self._emit_quality_events(
                cursor,
                study_id=study_id,
                prediction_class=prediction_class,
                confidence=confidence,
                quality_messages=quality_messages,
            )

        return {
            "prediction": prediction,
            "study_id": study_id,
            "created_at": created_at.isoformat(),
            "quality_status": quality_status,
            "image_object_key": image_object_key,
            "report_bucket": self._storage.bucket,
            "report_object_key": report_object_key,
            "events": events,
        }

    def list_history(self, limit: int) -> list[dict[str, Any]]:
        with self._db.read_cursor() as cursor:
            return radiology_repository.list_recent(cursor, limit)

    def get(self, study_id: str) -> dict[str, Any]:
        with self._db.read_cursor() as cursor:
            record = radiology_repository.get_by_id(cursor, study_id)
        if not record:
            raise RadiologyStudyNotFoundError(study_id)
        return record

    def get_report(self, study_id: str) -> dict[str, Any]:
        record = self.get(study_id)
        return self._storage.get_json(record["report_object_key"])

    def _persist_image(
        self,
        *,
        source_object_key: str | None,
        study_id: str,
        original_filename: str,
        content_type: str,
        image_bytes: bytes,
    ) -> str:
        if source_object_key:
            return source_object_key
        extension = os.path.splitext(original_filename)[1].lower() or ".jpg"
        object_key = f"uploads/{study_id}{extension}"
        self._storage.put_bytes(object_key, image_bytes, content_type)
        return object_key

    def _build_report(
        self,
        *,
        study_id: str,
        created_at: datetime,
        original_filename: str,
        content_type: str,
        image_bytes: bytes,
        checksum_sha256: str,
        image_object_key: str,
        prediction: dict[str, Any],
        prediction_class: str,
        confidence: float,
        quality_status: str,
        quality_messages: list[str],
        report_object_key: str,
    ) -> dict[str, Any]:
        alerts: list[str] = []
        if prediction_class == self.CRITICAL_PREDICTION_CLASS:
            alerts.append("Priorizar revision medica y activar protocolo de enfermedad contagiosa.")
        if confidence < self.LOW_CONFIDENCE_THRESHOLD:
            alerts.append("Enviar a cola de revision por baja confianza del modelo.")
        if quality_messages:
            alerts.append("Repetir o validar estudio por posibles problemas de calidad.")

        return {
            "study_id": study_id,
            "created_at": created_at.isoformat(),
            "image": {
                "original_filename": original_filename,
                "content_type": content_type,
                "file_size_bytes": len(image_bytes),
                "checksum_sha256": checksum_sha256,
                "bucket": self._storage.bucket,
                "object_key": image_object_key,
            },
            "prediction": prediction,
            "quality": {
                "status": quality_status,
                "messages": quality_messages,
            },
            "automation": {
                "report_object_key": report_object_key,
                "alerts": alerts,
            },
        }

    def _emit_quality_events(
        self,
        cursor,
        *,
        study_id: str,
        prediction_class: str,
        confidence: float,
        quality_messages: list[str],
    ) -> list[dict[str, Any]]:
        events: list[dict[str, Any]] = []
        if prediction_class == self.CRITICAL_PREDICTION_CLASS:
            events.append(
                self._quality.record(
                    cursor,
                    source="radiology",
                    severity="high",
                    event_type="clinical_alert",
                    message="Radiografia clasificada como COVID-19: requiere revision prioritaria.",
                    metadata={"study_id": study_id, "confidence": confidence},
                )
            )
        if confidence < self.LOW_CONFIDENCE_THRESHOLD:
            events.append(
                self._quality.record(
                    cursor,
                    source="radiology",
                    severity="medium",
                    event_type="low_model_confidence",
                    message="Prediccion radiologica con baja confianza.",
                    metadata={"study_id": study_id, "confidence": confidence},
                )
            )
        if quality_messages:
            events.append(
                self._quality.record(
                    cursor,
                    source="radiology",
                    severity="medium",
                    event_type="image_quality",
                    message="Estudio radiologico con advertencias de calidad.",
                    metadata={"study_id": study_id, "messages": quality_messages},
                )
            )
        return events

    @staticmethod
    def _safe_list(value: Any) -> list[str]:
        if isinstance(value, list):
            return [str(item) for item in value]
        return []
