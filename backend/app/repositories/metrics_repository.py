from __future__ import annotations

from typing import Any

import psycopg


RADIOLOGY_SUMMARY = """
SELECT
    COUNT(*) AS total_studies,
    COUNT(*) FILTER (WHERE prediction_class = 'Sana') AS healthy_count,
    COUNT(*) FILTER (WHERE prediction_class = 'Neumonia') AS pneumonia_count,
    COUNT(*) FILTER (WHERE prediction_class = 'COVID-19') AS covid_count,
    COUNT(*) FILTER (WHERE quality_status <> 'accepted') AS warning_count,
    COALESCE(AVG(confidence), 0) AS average_confidence,
    MAX(created_at) AS last_study_at
FROM radiology_studies;
"""

TRIAGE_COUNT = "SELECT COUNT(*) AS total_triage FROM triage_records;"

LATEST_PIPELINE_RUN = """
SELECT id, created_at, finished_at, status, input_uri,
       processed_count, rejected_count, report_bucket, report_object_key, metadata
FROM pipeline_runs
ORDER BY created_at DESC
LIMIT 1;
"""


def radiology_summary(cursor: psycopg.Cursor) -> dict[str, Any]:
    cursor.execute(RADIOLOGY_SUMMARY)
    row = cursor.fetchone()
    last_study_at = row["last_study_at"]
    return {
        "total_studies": row["total_studies"],
        "class_distribution": {
            "Sana": row["healthy_count"],
            "Neumonia": row["pneumonia_count"],
            "COVID-19": row["covid_count"],
        },
        "warning_count": row["warning_count"],
        "average_confidence": round(float(row["average_confidence"] or 0), 4),
        "last_study_at": last_study_at.isoformat() if last_study_at else None,
    }


def triage_count(cursor: psycopg.Cursor) -> int:
    cursor.execute(TRIAGE_COUNT)
    return cursor.fetchone()["total_triage"]


def latest_pipeline_run(cursor: psycopg.Cursor) -> dict[str, Any] | None:
    cursor.execute(LATEST_PIPELINE_RUN)
    row = cursor.fetchone()
    if not row:
        return None
    return {
        "run_id": row["id"],
        "created_at": row["created_at"].isoformat(),
        "finished_at": row["finished_at"].isoformat() if row["finished_at"] else None,
        "status": row["status"],
        "input_uri": row["input_uri"],
        "processed_count": row["processed_count"],
        "rejected_count": row["rejected_count"],
        "report_bucket": row["report_bucket"],
        "report_object_key": row["report_object_key"],
        "metadata": row["metadata"],
    }
