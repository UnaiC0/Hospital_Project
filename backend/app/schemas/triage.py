from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field


class TriageRequest(BaseModel):
    symptoms: list[str] = Field(default_factory=list)
    vitals: dict[str, Any] = Field(default_factory=dict)
    notes: str | None = None


class TriageAssessment(BaseModel):
    model_name: str
    model_version: str | None = None
    model_family: str | None = None
    risk_level: str
    recommended_priority: str
    confidence: float
    score: int
    probabilities: dict[str, float] | None = None
    top_contributors: list[dict[str, Any]] | None = None
    alerts: list[str] | None = None
    clinical_note: str | None = None


class TriageStorageInfo(BaseModel):
    postgres_database: str
    minio_bucket: str
    minio_object_key: str


class TriageQualityEvent(BaseModel):
    event_id: str
    created_at: str
    source: str
    severity: str
    event_type: str
    message: str
    metadata: dict[str, Any] = Field(default_factory=dict)


class TriageResponse(BaseModel):
    status: str
    triage_id: str
    created_at: str
    patient_assessment: TriageAssessment
    storage: TriageStorageInfo
    events: list[TriageQualityEvent] = Field(default_factory=list)


class TriageHistoryItem(BaseModel):
    triage_id: str
    created_at: str
    risk_level: str
    recommended_priority: str
    score: int
    confidence: float
    report_bucket: str
    report_object_key: str


class TriageHistoryResponse(BaseModel):
    count: int
    items: list[TriageHistoryItem]
