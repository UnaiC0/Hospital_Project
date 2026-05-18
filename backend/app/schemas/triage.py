from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field


class TriageRequest(BaseModel):
    symptoms: list[str] = Field(default_factory=list)
    vitals: dict[str, Any] = Field(default_factory=dict)
    notes: str | None = None


class TriageAssessment(BaseModel):
    model_name: str
    risk_level: str
    recommended_priority: str
    confidence: float
    score: int


class TriageStorageInfo(BaseModel):
    postgres_database: str
    minio_bucket: str
    minio_object_key: str


class TriageResponse(BaseModel):
    status: str
    triage_id: str
    created_at: str
    patient_assessment: TriageAssessment
    storage: TriageStorageInfo


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
