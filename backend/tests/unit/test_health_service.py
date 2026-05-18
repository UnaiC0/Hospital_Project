from __future__ import annotations

import pytest

from app.api.deps import get_settings
from app.services.health_service import HealthService


@pytest.fixture
def settings():
    return get_settings()


@pytest.fixture
def service(settings, fake_db, fake_storage) -> HealthService:
    return HealthService(settings, fake_db, fake_storage)


class TestReport:
    def test_ok_when_both_components_healthy(self, service):
        report = service.report()
        assert report["status"] == "ok"
        assert report["services"]["postgres"] == "ok"
        assert report["services"]["minio"] == "ok"

    def test_degraded_when_postgres_fails(self, fake_db, fake_storage, settings):
        # Force cursor.execute to raise
        def boom(*args, **kwargs):
            raise RuntimeError("connection refused")
        fake_db.cursor.execute = boom  # type: ignore[method-assign]
        service = HealthService(settings, fake_db, fake_storage)
        report = service.report()
        assert report["status"] == "degraded"
        assert "error" in report["services"]["postgres"]

    def test_degraded_when_minio_fails(self, fake_db, fake_storage, settings):
        def boom() -> None:
            raise RuntimeError("bucket missing")
        fake_storage.ensure_bucket = boom  # type: ignore[method-assign]
        service = HealthService(settings, fake_db, fake_storage)
        report = service.report()
        assert report["status"] == "degraded"
        assert "error" in report["services"]["minio"]

    def test_storage_block_includes_config(self, service, settings):
        report = service.report()
        assert report["storage"]["minio_bucket"] == settings.object_storage.bucket_name
        assert report["storage"]["postgres_database"] == settings.postgres.database
