from __future__ import annotations

from datetime import datetime
from typing import Any


def build_success_report(
    *,
    run_id: str,
    created_at: datetime,
    finished_at: datetime,
    input_uri: str,
    output_uri: str,
    processed_count: int,
    rejected_count: int,
    required_columns: tuple[str, ...],
    valid_labels: tuple[str, ...],
    duplicate_object_keys: list[str],
    class_distribution: dict[str, int],
    rejected_samples: list[dict[str, Any]],
) -> dict[str, Any]:
    return {
        "run_id": run_id,
        "created_at": created_at.isoformat(),
        "finished_at": finished_at.isoformat(),
        "status": "completed_with_warnings" if rejected_count else "completed",
        "input_uri": input_uri,
        "output_uri": output_uri,
        "processed_count": processed_count,
        "rejected_count": rejected_count,
        "metadata": {
            "required_columns": list(required_columns),
            "valid_labels": list(valid_labels),
            "duplicate_object_keys": duplicate_object_keys,
            "class_distribution": class_distribution,
            "rejected_samples": rejected_samples,
        },
    }


def build_failure_report(
    *,
    run_id: str,
    created_at: datetime,
    finished_at: datetime,
    input_uri: str,
    output_uri: str,
    error: str,
) -> dict[str, Any]:
    return {
        "run_id": run_id,
        "created_at": created_at.isoformat(),
        "finished_at": finished_at.isoformat(),
        "status": "failed",
        "input_uri": input_uri,
        "output_uri": output_uri,
        "processed_count": 0,
        "rejected_count": 0,
        "metadata": {"error": error},
    }
