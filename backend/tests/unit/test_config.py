from __future__ import annotations

import importlib

import pytest

from app.core import config as config_module


def test_get_settings_loads_required_env(monkeypatch):
    monkeypatch.setenv("POSTGRES_USER", "u")
    monkeypatch.setenv("POSTGRES_PASSWORD", "p")
    monkeypatch.setenv("POSTGRES_DB", "d")
    monkeypatch.setenv("MINIO_ENDPOINT", "http://m:9000")
    monkeypatch.setenv("MINIO_ACCESS_KEY", "a")
    monkeypatch.setenv("MINIO_SECRET_KEY", "s")
    monkeypatch.setenv("MINIO_BUCKET_NAME", "b")
    importlib.reload(config_module)
    settings = config_module.get_settings()
    assert settings.postgres.user == "u"
    assert settings.postgres.password == "p"
    assert settings.postgres.database == "d"
    assert settings.object_storage.endpoint == "http://m:9000"
    assert settings.object_storage.bucket_name == "b"


def test_get_settings_raises_when_required_missing(monkeypatch):
    monkeypatch.delenv("POSTGRES_USER", raising=False)
    importlib.reload(config_module)
    with pytest.raises(config_module.ConfigurationError):
        config_module.get_settings()


def test_get_settings_auto_create_bucket_default(monkeypatch):
    for key in [
        "POSTGRES_USER", "POSTGRES_PASSWORD", "POSTGRES_DB",
        "MINIO_ENDPOINT", "MINIO_ACCESS_KEY", "MINIO_SECRET_KEY", "MINIO_BUCKET_NAME",
    ]:
        monkeypatch.setenv(key, "x")
    monkeypatch.delenv("MINIO_AUTO_CREATE_BUCKET", raising=False)
    importlib.reload(config_module)
    settings = config_module.get_settings()
    assert settings.object_storage.auto_create_bucket is False
