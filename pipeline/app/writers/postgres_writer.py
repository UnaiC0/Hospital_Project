from __future__ import annotations

import json
from datetime import datetime, timezone
from typing import Any
from uuid import uuid4

import psycopg

from app.core.config import PostgresSettings


INSERT_RUN = """
INSERT INTO pipeline_runs (
    id, created_at, finished_at, status, input_uri,
    processed_count, rejected_count, report_bucket, report_object_key, metadata
)
VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s::jsonb);
"""


INSERT_EVENT = """
INSERT INTO quality_events (
    id, created_at, source, severity, event_type, message, metadata
)
VALUES (%s, %s, %s, %s, %s, %s, %s::jsonb);
"""


class PostgresWriter:
    """Persists pipeline outcomes inside a single transaction so a partial
    failure leaves no half-committed state."""

    def __init__(self, settings: PostgresSettings):
        self._settings = settings

    def _connect(self) -> psycopg.Connection:
        return psycopg.connect(
            host=self._settings.host,
            port=self._settings.port,
            user=self._settings.user,
            password=self._settings.password,
            dbname=self._settings.database,
            connect_timeout=self._settings.connect_timeout_seconds,
        )

    def persist_run(self, *, report: dict[str, Any], report_object_key: str, bucket: str) -> None:
        with self._connect() as connection:
            with connection.cursor() as cursor:
                cursor.execute(
                    INSERT_RUN,
                    (
                        report["run_id"],
                        report["created_at"],
                        report["finished_at"],
                        report["status"],
                        report["input_uri"],
                        report["processed_count"],
                        report["rejected_count"],
                        bucket,
                        report_object_key,
                        json.dumps(report["metadata"]),
                    ),
                )
            connection.commit()

    def record_quality_event(
        self,
        *,
        report: dict[str, Any],
        severity: str,
        event_type: str,
        message: str,
    ) -> None:
        metadata = {
            "run_id": report["run_id"],
            "input_uri": report["input_uri"],
            "rejected_count": report["rejected_count"],
            "processed_count": report["processed_count"],
        }
        with self._connect() as connection:
            with connection.cursor() as cursor:
                cursor.execute(
                    INSERT_EVENT,
                    (
                        str(uuid4()),
                        datetime.now(timezone.utc),
                        "pipeline",
                        severity,
                        event_type,
                        message,
                        json.dumps(metadata),
                    ),
                )
            connection.commit()
