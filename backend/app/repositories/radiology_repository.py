from __future__ import annotations

import json
from datetime import datetime
from typing import Any

import psycopg


INSERT_STUDY = """
INSERT INTO radiology_studies (
    id, created_at, original_filename, content_type,
    file_size_bytes, checksum_sha256, image_bucket, image_object_key,
    prediction_class, probabilities, model_name, model_version,
    confidence, quality_status, quality_messages, model_response,
    report_bucket, report_object_key
)
VALUES (
    %s, %s, %s, %s, %s, %s, %s, %s, %s, %s::jsonb, %s, %s,
    %s, %s, %s::jsonb, %s::jsonb, %s, %s
);
"""


SELECT_RECENT = """
SELECT id, created_at, original_filename, content_type,
       file_size_bytes, image_bucket, image_object_key,
       prediction_class, probabilities, model_name, model_version,
       confidence, quality_status, quality_messages,
       report_bucket, report_object_key
FROM radiology_studies
ORDER BY created_at DESC
LIMIT %s;
"""


SELECT_BY_ID = """
SELECT id, created_at, original_filename, content_type,
       file_size_bytes, checksum_sha256, image_bucket, image_object_key,
       prediction_class, probabilities, model_name, model_version,
       confidence, quality_status, quality_messages, model_response,
       report_bucket, report_object_key
FROM radiology_studies
WHERE id = %s;
"""


def insert(
    cursor: psycopg.Cursor,
    *,
    study_id: str,
    created_at: datetime,
    original_filename: str,
    content_type: str,
    file_size_bytes: int,
    checksum_sha256: str,
    image_bucket: str,
    image_object_key: str,
    prediction_class: str,
    probabilities: dict[str, float],
    model_name: str,
    model_version: str,
    confidence: float,
    quality_status: str,
    quality_messages: list[str],
    model_response: dict[str, Any],
    report_bucket: str,
    report_object_key: str,
) -> None:
    cursor.execute(
        INSERT_STUDY,
        (
            study_id,
            created_at,
            original_filename,
            content_type,
            file_size_bytes,
            checksum_sha256,
            image_bucket,
            image_object_key,
            prediction_class,
            json.dumps(probabilities),
            model_name,
            model_version,
            confidence,
            quality_status,
            json.dumps(quality_messages),
            json.dumps(model_response),
            report_bucket,
            report_object_key,
        ),
    )


def list_recent(cursor: psycopg.Cursor, limit: int) -> list[dict[str, Any]]:
    cursor.execute(SELECT_RECENT, (limit,))
    return [
        {
            "study_id": row["id"],
            "created_at": row["created_at"].isoformat(),
            "original_filename": row["original_filename"],
            "content_type": row["content_type"],
            "file_size_bytes": row["file_size_bytes"],
            "image_bucket": row["image_bucket"],
            "image_object_key": row["image_object_key"],
            "prediction_class": row["prediction_class"],
            "probabilities": row["probabilities"],
            "model_name": row["model_name"],
            "model_version": row["model_version"],
            "confidence": row["confidence"],
            "quality_status": row["quality_status"],
            "quality_messages": row["quality_messages"],
            "report_bucket": row["report_bucket"],
            "report_object_key": row["report_object_key"],
        }
        for row in cursor.fetchall()
    ]


def get_by_id(cursor: psycopg.Cursor, study_id: str) -> dict[str, Any] | None:
    cursor.execute(SELECT_BY_ID, (study_id,))
    row = cursor.fetchone()
    if not row:
        return None
    return {
        "study_id": row["id"],
        "created_at": row["created_at"].isoformat(),
        "original_filename": row["original_filename"],
        "content_type": row["content_type"],
        "file_size_bytes": row["file_size_bytes"],
        "checksum_sha256": row["checksum_sha256"],
        "image_bucket": row["image_bucket"],
        "image_object_key": row["image_object_key"],
        "prediction_class": row["prediction_class"],
        "probabilities": row["probabilities"],
        "model": {
            "name": row["model_name"],
            "version": row["model_version"],
            "response": row["model_response"],
        },
        "confidence": row["confidence"],
        "quality_status": row["quality_status"],
        "quality_messages": row["quality_messages"],
        "report_bucket": row["report_bucket"],
        "report_object_key": row["report_object_key"],
    }
