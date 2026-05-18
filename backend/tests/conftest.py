"""Global test fixtures.

The top-level statements run before pytest imports any test module. We set
the required environment variables here so that app.core.config.get_settings()
succeeds the first time it is called from anywhere in the test process.
"""

from __future__ import annotations

import os
import sys
from pathlib import Path

# 1. Make `app` importable when pytest is launched from backend/ root.
BACKEND_ROOT = Path(__file__).resolve().parent.parent
if str(BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(BACKEND_ROOT))

# 2. Populate env BEFORE any `from app...` import happens.
os.environ.setdefault("POSTGRES_USER", "test_user")
os.environ.setdefault("POSTGRES_PASSWORD", "test_password")
os.environ.setdefault("POSTGRES_DB", "test_db")
os.environ.setdefault("MINIO_ENDPOINT", "http://minio.test:9000")
os.environ.setdefault("MINIO_ACCESS_KEY", "test_access")
os.environ.setdefault("MINIO_SECRET_KEY", "test_secret")
os.environ.setdefault("MINIO_BUCKET_NAME", "test-bucket")
os.environ.setdefault("MINIO_AUTO_CREATE_BUCKET", "true")
os.environ.setdefault("SPARK_MASTER_URL", "spark://test:7077")

import pytest

from app.api import deps
from app.main import create_app
from tests.helpers.fakes import (
    FakeDatabaseSession,
    FakeObjectStorage,
    StubInferenceService,
)


@pytest.fixture
def fake_db():
    return FakeDatabaseSession()


@pytest.fixture
def fake_storage():
    return FakeObjectStorage()


@pytest.fixture
def stub_inference():
    return StubInferenceService()


@pytest.fixture
def app(fake_db, fake_storage, stub_inference):
    """A fresh FastAPI app per test, with all external collaborators replaced
    by in-memory fakes via FastAPI dependency_overrides."""
    application = create_app()

    from app.services.health_service import HealthService
    from app.services.metrics_service import MetricsService
    from app.services.quality_service import QualityService
    from app.services.radiology_service import RadiologyService
    from app.services.triage_service import TriageService

    quality_service = QualityService(fake_db)
    triage_service = TriageService(fake_db, fake_storage)
    radiology_service = RadiologyService(
        db_session=fake_db,
        object_storage=fake_storage,
        inference_service=stub_inference,
        quality_service=quality_service,
    )
    metrics_service = MetricsService(fake_db)
    health_service = HealthService(
        settings=deps.get_settings(),
        db_session=fake_db,
        object_storage=fake_storage,
    )

    application.dependency_overrides[deps.get_database_session] = lambda: fake_db
    application.dependency_overrides[deps.get_object_storage] = lambda: fake_storage
    application.dependency_overrides[deps.get_inference_service] = lambda: stub_inference
    application.dependency_overrides[deps.get_quality_service] = lambda: quality_service
    application.dependency_overrides[deps.get_triage_service] = lambda: triage_service
    application.dependency_overrides[deps.get_radiology_service] = lambda: radiology_service
    application.dependency_overrides[deps.get_metrics_service] = lambda: metrics_service
    application.dependency_overrides[deps.get_health_service] = lambda: health_service

    yield application

    application.dependency_overrides.clear()


@pytest.fixture
def client(app):
    """TestClient without context-manager use — lifespan stays inert
    so we never hit Postgres in unit tests."""
    from fastapi.testclient import TestClient
    return TestClient(app)
