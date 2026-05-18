from __future__ import annotations

from typing import Any

from pydantic import BaseModel


class RadiologyMetrics(BaseModel):
    total_studies: int
    class_distribution: dict[str, int]
    warning_count: int
    average_confidence: float
    last_study_at: str | None


class TriageMetrics(BaseModel):
    total_records: int


class PipelineRunSummary(BaseModel):
    run_id: str
    created_at: str
    finished_at: str | None
    status: str
    input_uri: str
    processed_count: int
    rejected_count: int
    report_bucket: str | None
    report_object_key: str | None
    metadata: dict[str, Any]


class PipelineMetrics(BaseModel):
    latest_run: PipelineRunSummary | None


class QualityMetrics(BaseModel):
    open_events_by_severity: dict[str, int]


class PlatformMetrics(BaseModel):
    radiology: RadiologyMetrics
    triage: TriageMetrics
    pipeline: PipelineMetrics
    quality: QualityMetrics
