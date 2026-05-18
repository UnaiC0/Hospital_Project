from __future__ import annotations

from pydantic import BaseModel


class HealthServices(BaseModel):
    inference_engine: str
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
