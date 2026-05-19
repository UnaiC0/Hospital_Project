from __future__ import annotations

from typing import Any

from app.core.config import Settings
from app.db.session import DatabaseSession
from app.services import triage_model
from app.storage.object_storage import ObjectStorage


class HealthService:
    def __init__(
        self,
        settings: Settings,
        db_session: DatabaseSession,
        object_storage: ObjectStorage,
    ):
        self._settings = settings
        self._db = db_session
        self._storage = object_storage

    def report(self) -> dict[str, Any]:
        postgres_status = self._postgres_status()
        minio_status = self._minio_status()
        overall = "ok" if postgres_status == "ok" and minio_status == "ok" else "degraded"

        return {
            "status": overall,
            "services": {
                "inference_engine": "embedded",
                "triage_model": triage_model.model_status(),
                "postgres": postgres_status,
                "minio": minio_status,
                "spark": self._settings.spark_master_url,
            },
            "storage": {
                "postgres_database": self._settings.postgres.database,
                "minio_endpoint": self._settings.object_storage.endpoint or "not-configured",
                "minio_region": self._settings.object_storage.region,
                "minio_bucket": self._settings.object_storage.bucket_name,
            },
        }

    def _postgres_status(self) -> str:
        try:
            with self._db.read_cursor() as cursor:
                cursor.execute("SELECT 1;")
                cursor.fetchone()
            return "ok"
        except Exception as exc:
            return f"error: {exc}"

    def _minio_status(self) -> str:
        try:
            self._storage.ensure_bucket()
            return "ok"
        except Exception as exc:
            return f"error: {exc}"
