from __future__ import annotations

from typing import Any

from pydantic import BaseModel


class RadiologyPrediction(BaseModel):
    model_name: str
    model_version: str
    model_family: str
    class_label: str
    probabilities: dict[str, float]
    confidence: float
    features: dict[str, Any]
    preprocessing: dict[str, Any]
    quality_flags: list[str]
    explanation: str
    clinical_note: str

    model_config = {"populate_by_name": True}


class RadiologyStorageInfo(BaseModel):
    postgres_database: str
    minio_bucket: str
    image_object_key: str | None
    report_object_key: str


class QualityEventSummary(BaseModel):
    event_id: str
    created_at: str
    source: str
    severity: str
    event_type: str
    message: str
    metadata: dict[str, Any]


class RadiologyPredictResponse(BaseModel):
    model_name: str
    model_version: str
    model_family: str
    class_label: str
    probabilities: dict[str, float]
    confidence: float
    features: dict[str, Any]
    preprocessing: dict[str, Any]
    quality_flags: list[str]
    explanation: str
    clinical_note: str
    study_id: str
    created_at: str
    quality_status: str
    storage: RadiologyStorageInfo
    events: list[QualityEventSummary]


class RadiologyHistoryItem(BaseModel):
    study_id: str
    created_at: str
    original_filename: str
    content_type: str
    file_size_bytes: int
    image_bucket: str | None
    image_object_key: str | None
    prediction_class: str
    probabilities: dict[str, float]
    model_name: str
    model_version: str
    confidence: float
    quality_status: str
    quality_messages: list[str]
    report_bucket: str
    report_object_key: str


class RadiologyHistoryResponse(BaseModel):
    count: int
    items: list[RadiologyHistoryItem]
