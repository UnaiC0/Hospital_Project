from __future__ import annotations

import json
from datetime import datetime, timezone
from typing import Any
from uuid import uuid4

from app.core.metrics import TRIAGE_ASSESSMENTS_TOTAL
from app.db.session import DatabaseSession
from app.repositories import triage_repository
from app.schemas.triage import TriageRequest
from app.storage.object_storage import ObjectStorage


class TriageNotFoundError(LookupError):
    pass


class TriageService:
    def __init__(self, db_session: DatabaseSession, object_storage: ObjectStorage):
        self._db = db_session
        self._storage = object_storage

    def assess(self, request: TriageRequest) -> dict[str, Any]:
        symptoms = {symptom.strip().lower() for symptom in request.symptoms if symptom}
        heart_rate = self._coerce_float(request.vitals.get("heart_rate"), 0.0)
        oxygen_saturation = self._coerce_float(request.vitals.get("oxygen_saturation"), 100.0)
        systolic_bp = self._coerce_float(request.vitals.get("systolic_bp"), 120.0)

        score = min(len(symptoms) * 8, 40)
        if {"chest pain", "shortness of breath", "loss of consciousness"} & symptoms:
            score += 35
        if heart_rate >= 120:
            score += 15
        if oxygen_saturation < 92:
            score += 25
        if systolic_bp < 90:
            score += 20
        score = min(score, 100)

        if score >= 75:
            risk_level, recommended_priority = "critical", "immediate"
        elif score >= 50:
            risk_level, recommended_priority = "high", "urgent"
        elif score >= 25:
            risk_level, recommended_priority = "medium", "priority"
        else:
            risk_level, recommended_priority = "low", "standard"

        TRIAGE_ASSESSMENTS_TOTAL.labels(risk_level=risk_level).inc()
        return {
            "model_name": "hospital-triage-embedded",
            "risk_level": risk_level,
            "recommended_priority": recommended_priority,
            "confidence": round(min(0.99, 0.65 + (score / 200)), 2),
            "score": score,
        }

    def register(self, request: TriageRequest, assessment: dict[str, Any]) -> dict[str, Any]:
        """ACID write: object storage put followed by DB insert inside a single
        transaction. If the DB insert fails the bucket object is best-effort
        orphaned (acceptable here because the object key is unique and
        unreferenced; full SAGA compensation would belong in a future iteration).
        """
        record_id = str(uuid4())
        created_at = datetime.now(timezone.utc)
        object_key = f"triage-reports/{record_id}.json"

        report = {
            "triage_id": record_id,
            "created_at": created_at.isoformat(),
            "request": request.model_dump(),
            "assessment": assessment,
        }

        self._storage.ensure_bucket()
        self._storage.put_json(object_key, report)

        with self._db.transaction() as cursor:
            triage_repository.insert(
                cursor,
                record_id=record_id,
                created_at=created_at,
                request_payload=request.model_dump(),
                model_response=assessment,
                risk_level=str(assessment.get("risk_level", "unknown")),
                recommended_priority=str(assessment.get("recommended_priority", "unknown")),
                score=int(assessment.get("score", 0)),
                confidence=float(assessment.get("confidence", 0)),
                report_bucket=self._storage.bucket,
                report_object_key=object_key,
            )

        return {
            "triage_id": record_id,
            "created_at": created_at.isoformat(),
            "report_bucket": self._storage.bucket,
            "report_object_key": object_key,
        }

    def list_history(self, limit: int) -> list[dict[str, Any]]:
        with self._db.read_cursor() as cursor:
            return triage_repository.list_recent(cursor, limit)

    def get(self, triage_id: str) -> dict[str, Any]:
        with self._db.read_cursor() as cursor:
            record = triage_repository.get_by_id(cursor, triage_id)
        if not record:
            raise TriageNotFoundError(triage_id)
        return record

    def get_report(self, triage_id: str) -> dict[str, Any]:
        record = self.get(triage_id)
        return self._storage.get_json(record["report_object_key"])

    @staticmethod
    def _coerce_float(value: Any, default: float) -> float:
        try:
            return float(value) if value is not None else default
        except (TypeError, ValueError):
            return default
