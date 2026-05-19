from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field


class HealthServices(BaseModel):
    inference_engine: str
    triage_model: dict[str, Any] = Field(default_factory=dict)
    postgres: str
    minio: str
    spark: str


class HealthStorage(BaseModel):
    postgres_database: str
    minio_endpoint: str
    minio_region: str
    minio_bucket: str


class HealthResponse(BaseModel):
    status: str
    services: HealthServices
    storage: HealthStorage
