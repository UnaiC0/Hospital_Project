from __future__ import annotations

import time

from app.core.logging import get_logger
from app.db.session import DatabaseSession

logger = get_logger(__name__)


SCHEMA_DDL = """
CREATE TABLE IF NOT EXISTS triage_records (
    id TEXT PRIMARY KEY,
    created_at TIMESTAMPTZ NOT NULL,
    request_payload JSONB NOT NULL,
    model_response JSONB NOT NULL,
    risk_level TEXT NOT NULL,
    recommended_priority TEXT NOT NULL,
    score INTEGER NOT NULL,
    confidence DOUBLE PRECISION NOT NULL,
    report_bucket TEXT NOT NULL,
    report_object_key TEXT NOT NULL
);

CREATE INDEX IF NOT EXISTS triage_records_created_at_idx
ON triage_records (created_at DESC);

CREATE TABLE IF NOT EXISTS radiology_studies (
    id TEXT PRIMARY KEY,
    created_at TIMESTAMPTZ NOT NULL,
    original_filename TEXT NOT NULL,
    content_type TEXT NOT NULL,
    file_size_bytes INTEGER NOT NULL,
    checksum_sha256 TEXT NOT NULL,
    image_bucket TEXT,
    image_object_key TEXT,
    prediction_class TEXT NOT NULL,
    probabilities JSONB NOT NULL,
    model_name TEXT NOT NULL,
    model_version TEXT NOT NULL,
    confidence DOUBLE PRECISION NOT NULL,
    quality_status TEXT NOT NULL,
    quality_messages JSONB NOT NULL,
    model_response JSONB NOT NULL,
    report_bucket TEXT NOT NULL,
    report_object_key TEXT NOT NULL
);

CREATE INDEX IF NOT EXISTS radiology_studies_created_at_idx
ON radiology_studies (created_at DESC);

CREATE INDEX IF NOT EXISTS radiology_studies_prediction_class_idx
ON radiology_studies (prediction_class);

CREATE TABLE IF NOT EXISTS quality_events (
    id TEXT PRIMARY KEY,
    created_at TIMESTAMPTZ NOT NULL,
    source TEXT NOT NULL,
    severity TEXT NOT NULL,
    event_type TEXT NOT NULL,
    message TEXT NOT NULL,
    metadata JSONB NOT NULL,
    resolved BOOLEAN NOT NULL DEFAULT FALSE
);

CREATE INDEX IF NOT EXISTS quality_events_created_at_idx
ON quality_events (created_at DESC);

CREATE TABLE IF NOT EXISTS pipeline_runs (
    id TEXT PRIMARY KEY,
    created_at TIMESTAMPTZ NOT NULL,
    finished_at TIMESTAMPTZ,
    status TEXT NOT NULL,
    input_uri TEXT NOT NULL,
    processed_count INTEGER NOT NULL DEFAULT 0,
    rejected_count INTEGER NOT NULL DEFAULT 0,
    report_bucket TEXT,
    report_object_key TEXT,
    metadata JSONB NOT NULL DEFAULT '{}'::jsonb
);

CREATE INDEX IF NOT EXISTS pipeline_runs_created_at_idx
ON pipeline_runs (created_at DESC);
"""


def initialize_schema(session: DatabaseSession) -> None:
    with session.transaction() as cursor:
        cursor.execute(SCHEMA_DDL)


def initialize_schema_with_retry(
    session: DatabaseSession,
    attempts: int,
    delay_seconds: float,
) -> None:
    last_error: Exception | None = None
    for attempt in range(1, attempts + 1):
        try:
            initialize_schema(session)
            logger.info("schema_initialized", extra={"attempt": attempt})
            return
        except Exception as exc:
            last_error = exc
            logger.warning(
                "schema_initialization_failed",
                extra={"attempt": attempt, "error": str(exc)},
            )
            if attempt == attempts:
                break
            time.sleep(delay_seconds)
    raise RuntimeError("PostgreSQL schema initialization failed") from last_error
