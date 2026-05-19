from __future__ import annotations

import json
from datetime import datetime
from typing import Any

import psycopg


INSERT_TRIAGE = """
INSERT INTO triage_records (
    id, created_at, patient_id, patient_name,
    request_payload, model_response,
    risk_level, recommended_priority, score, confidence,
    report_bucket, report_object_key
)
VALUES (%s, %s, %s, %s, %s::jsonb, %s::jsonb, %s, %s, %s, %s, %s, %s);
"""


SELECT_RECENT = """
SELECT id, created_at, patient_id, patient_name, risk_level, recommended_priority,
       score, confidence, report_bucket, report_object_key
FROM triage_records
ORDER BY created_at DESC
LIMIT %s;
"""


SELECT_BY_ID = """
SELECT id, created_at, patient_id, patient_name, request_payload, model_response,
       risk_level, recommended_priority, score, confidence,
       report_bucket, report_object_key
FROM triage_records
WHERE id = %s;
"""


def insert(
    cursor: psycopg.Cursor,
    *,
    record_id: str,
    created_at: datetime,
    patient_id: str,
    patient_name: str,
    request_payload: dict[str, Any],
    model_response: dict[str, Any],
    risk_level: str,
    recommended_priority: str,
    score: int,
    confidence: float,
    report_bucket: str,
    report_object_key: str,
) -> None:
    cursor.execute(
        INSERT_TRIAGE,
        (
            record_id,
            created_at,
            patient_id,
            patient_name,
            json.dumps(request_payload),
            json.dumps(model_response),
            risk_level,
            recommended_priority,
            score,
            confidence,
            report_bucket,
            report_object_key,
        ),
    )


def list_recent(cursor: psycopg.Cursor, limit: int) -> list[dict[str, Any]]:
    cursor.execute(SELECT_RECENT, (limit,))
    return [
        {
            "triage_id": row["id"],
            "patient_id": row["patient_id"],
            "patient_name": row["patient_name"],
            "created_at": row["created_at"].isoformat(),
            "risk_level": row["risk_level"],
            "recommended_priority": row["recommended_priority"],
            "score": row["score"],
            "confidence": row["confidence"],
            "report_bucket": row["report_bucket"],
            "report_object_key": row["report_object_key"],
        }
        for row in cursor.fetchall()
    ]


def get_by_id(cursor: psycopg.Cursor, triage_id: str) -> dict[str, Any] | None:
    cursor.execute(SELECT_BY_ID, (triage_id,))
    row = cursor.fetchone()
    if not row:
        return None
    return {
        "triage_id": row["id"],
        "patient_id": row["patient_id"],
        "patient_name": row["patient_name"],
        "created_at": row["created_at"].isoformat(),
        "request": row["request_payload"],
        "assessment": row["model_response"],
        "risk_level": row["risk_level"],
        "recommended_priority": row["recommended_priority"],
        "score": row["score"],
        "confidence": row["confidence"],
        "report_bucket": row["report_bucket"],
        "report_object_key": row["report_object_key"],
    }
