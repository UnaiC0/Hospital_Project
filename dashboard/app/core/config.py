from __future__ import annotations

import os
from dataclasses import dataclass, field
from functools import lru_cache
from pathlib import Path


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
class BackendSettings:
    base_url: str


@dataclass(frozen=True)
class ObjectStorageSettings:
    endpoint: str
    access_key: str
    secret_key: str
    region: str
    bucket_name: str
    console_url: str


@dataclass(frozen=True)
class SessionSettings:
    secret_key: str
    cookie_secure: bool


@dataclass(frozen=True)
class UploadSettings:
    max_file_size_bytes: int = 5 * 1024 * 1024
    allowed_extensions: frozenset[str] = field(
        default_factory=lambda: frozenset({"jpg", "jpeg", "png"})
    )


@dataclass(frozen=True)
class UserCredentials:
    username: str
    password_hash: str
    role: str
    display_name: str


@dataclass(frozen=True)
class Settings:
    backend: BackendSettings
    object_storage: ObjectStorageSettings
    session: SessionSettings
    upload: UploadSettings
    users: tuple[UserCredentials, ...]


def _load_local_env() -> None:
    env_path = Path(__file__).resolve().parents[2] / ".env"
    if not env_path.exists():
        return
    try:
        from dotenv import load_dotenv
        load_dotenv(env_path)
        return
    except ImportError:
        pass
    for raw_line in env_path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        os.environ.setdefault(key.strip(), value.strip().strip("\"'"))


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    _load_local_env()

    admin = UserCredentials(
        username=_required("ADMIN_USERNAME"),
        password_hash=_required("ADMIN_PASSWORD_HASH"),
        role="admin",
        display_name="Administrador",
    )
    doctor = UserCredentials(
        username=_required("USER_USERNAME"),
        password_hash=_required("USER_PASSWORD_HASH"),
        role="user",
        display_name="Doctor",
    )
    if admin.username == doctor.username:
        raise ConfigurationError("ADMIN_USERNAME and USER_USERNAME must differ")

    return Settings(
        backend=BackendSettings(
            base_url=_optional("BACKEND_URL", "http://backend:8000").rstrip("/"),
        ),
        object_storage=ObjectStorageSettings(
            endpoint=_optional("MINIO_ENDPOINT", "http://minio:9000").rstrip("/"),
            access_key=_optional("MINIO_ACCESS_KEY", "") or _required("MINIO_ROOT_USER"),
            secret_key=_optional("MINIO_SECRET_KEY", "") or _required("MINIO_ROOT_PASSWORD"),
            region=_optional("MINIO_REGION", "us-east-1"),
            bucket_name=_required("MINIO_BUCKET_NAME"),
            console_url=_optional("MINIO_CONSOLE_URL", "http://localhost:9001").rstrip("/"),
        ),
        session=SessionSettings(
            secret_key=_required("SECRET_KEY"),
            cookie_secure=_bool("SESSION_COOKIE_SECURE", False),
        ),
        upload=UploadSettings(),
        users=(admin, doctor),
    )
