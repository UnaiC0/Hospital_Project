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
    if value is None or value == "":
        return default
    return value


def _bool(name: str, default: bool) -> bool:
    value = os.getenv(name)
    if value is None or value == "":
        return default
    return value.strip().lower() in {"1", "true", "yes", "on"}


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
    auto_create_bucket: bool


@dataclass(frozen=True)
class InferenceSettings:
    max_file_size_bytes: int = 5 * 1024 * 1024
    allowed_extensions: frozenset[str] = field(
        default_factory=lambda: frozenset({".jpg", ".jpeg", ".png"})
    )
    allowed_mime_types: frozenset[str] = field(
        default_factory=lambda: frozenset({"image/jpeg", "image/png"})
    )


@dataclass(frozen=True)
class Settings:
    postgres: PostgresSettings
    object_storage: ObjectStorageSettings
    inference: InferenceSettings
    spark_master_url: str
    schema_init_attempts: int = 10
    schema_init_delay_seconds: float = 2.0


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
            auto_create_bucket=_bool("MINIO_AUTO_CREATE_BUCKET", False),
        ),
        inference=InferenceSettings(),
        spark_master_url=_optional("SPARK_MASTER_URL", "spark://spark:7077"),
    )
