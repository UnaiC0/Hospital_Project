from __future__ import annotations

import os
from dataclasses import dataclass, field
from functools import lru_cache


class ConfigurationError(RuntimeError):
    pass


def _required(name: str) -> str:
    value = os.getenv(name)
    if value is None or value == "":
        raise ConfigurationError(f"Missing required environment variable: {name}")
    return value


def _optional(name: str, default: str) -> str:
    value = os.getenv(name)
    return value if value not in (None, "") else default


@dataclass(frozen=True)
class PostgresSettings:
    host: str
    port: str
    user: str
    password: str
    database: str
    connect_timeout_seconds: int = 5


@dataclass(frozen=True)
class ObjectStorageSettings:
    endpoint: str
    access_key: str
    secret_key: str
    region: str
    bucket_name: str


@dataclass(frozen=True)
class PipelinePaths:
    input_path: str
    output_path: str


@dataclass(frozen=True)
class SchemaRules:
    required_columns: tuple[str, ...] = (
        "study_id",
        "patient_age",
        "patient_sex",
        "image_object_key",
        "label",
        "acquisition_date",
        "source",
    )
    valid_labels: tuple[str, ...] = ("Sana", "Neumonia", "COVID-19")


@dataclass(frozen=True)
class Settings:
    postgres: PostgresSettings
    object_storage: ObjectStorageSettings
    paths: PipelinePaths
    schema_rules: SchemaRules = field(default_factory=SchemaRules)


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    return Settings(
        postgres=PostgresSettings(
            host=_optional("POSTGRES_HOST", "db"),
            port=_optional("POSTGRES_PORT", "5432"),
            user=_required("POSTGRES_USER"),
            password=_required("POSTGRES_PASSWORD"),
            database=_required("POSTGRES_DB"),
        ),
        object_storage=ObjectStorageSettings(
            endpoint=_required("MINIO_ENDPOINT"),
            access_key=_required("MINIO_ACCESS_KEY"),
            secret_key=_required("MINIO_SECRET_KEY"),
            region=_optional("MINIO_REGION", "us-east-1"),
            bucket_name=_required("MINIO_BUCKET_NAME"),
        ),
        paths=PipelinePaths(
            input_path=_optional("PIPELINE_INPUT_PATH", "/data/incoming/radiology_studies.csv"),
            output_path=_optional("PIPELINE_OUTPUT_PATH", "/data/processed/radiology_clean"),
        ),
    )
