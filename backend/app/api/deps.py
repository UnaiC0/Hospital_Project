from __future__ import annotations

from functools import lru_cache

from app.core.config import Settings, get_settings
from app.db.session import DatabaseSession, build_database_session
from app.services.health_service import HealthService
from app.services.inference_service import InferenceService, build_inference_service
from app.services.metrics_service import MetricsService
from app.services.quality_service import QualityService
from app.services.radiology_service import RadiologyService
from app.services.triage_service import TriageService
from app.storage.object_storage import ObjectStorage, build_object_storage


@lru_cache(maxsize=1)
def get_database_session() -> DatabaseSession:
    return build_database_session()


@lru_cache(maxsize=1)
def get_object_storage() -> ObjectStorage:
    return build_object_storage()


@lru_cache(maxsize=1)
def get_inference_service() -> InferenceService:
    return build_inference_service()


@lru_cache(maxsize=1)
def get_quality_service() -> QualityService:
    return QualityService(get_database_session())


@lru_cache(maxsize=1)
def get_triage_service() -> TriageService:
    return TriageService(
        db_session=get_database_session(),
        object_storage=get_object_storage(),
        quality_service=get_quality_service(),
    )


@lru_cache(maxsize=1)
def get_radiology_service() -> RadiologyService:
    return RadiologyService(
        db_session=get_database_session(),
        object_storage=get_object_storage(),
        inference_service=get_inference_service(),
        quality_service=get_quality_service(),
    )


@lru_cache(maxsize=1)
def get_metrics_service() -> MetricsService:
    return MetricsService(get_database_session())


@lru_cache(maxsize=1)
def get_health_service() -> HealthService:
    return HealthService(
        settings=get_settings(),
        db_session=get_database_session(),
        object_storage=get_object_storage(),
    )


def get_app_settings() -> Settings:
    return get_settings()
