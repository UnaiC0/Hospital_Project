from __future__ import annotations

from typing import Any

from fastapi import APIRouter, Depends, File, Form, Query, UploadFile
from fastapi.concurrency import run_in_threadpool

from app.api.deps import get_app_settings, get_radiology_service
from app.core.config import Settings
from app.schemas.radiology import RadiologyHistoryResponse
from app.services.radiology_service import RadiologyService
from app.utils import image_validation

router = APIRouter(tags=["radiology"])


@router.post("/predict")
async def predict(
    file: UploadFile = File(...),
    source_object_key: str | None = Form(default=None),
    service: RadiologyService = Depends(get_radiology_service),
    settings: Settings = Depends(get_app_settings),
) -> dict[str, Any]:
    try:
        image_bytes = await file.read()
        image_validation.validate(
            filename=file.filename or "",
            content_type=file.content_type,
            image_bytes=image_bytes,
            settings=settings.inference,
        )
        result = await run_in_threadpool(
            service.predict_and_register,
            original_filename=file.filename or "unknown",
            content_type=file.content_type or "application/octet-stream",
            image_bytes=image_bytes,
            source_object_key=source_object_key,
        )
    finally:
        await file.close()

    prediction = result["prediction"]
    return {
        **prediction,
        "study_id": result["study_id"],
        "created_at": result["created_at"],
        "quality_status": result["quality_status"],
        "storage": {
            "postgres_database": settings.postgres.database,
            "minio_bucket": result["report_bucket"],
            "image_object_key": result["image_object_key"],
            "report_object_key": result["report_object_key"],
        },
        "events": result["events"],
    }


@router.get("/studies/history", response_model=RadiologyHistoryResponse)
async def studies_history(
    limit: int = Query(default=10, ge=1, le=100),
    service: RadiologyService = Depends(get_radiology_service),
) -> dict[str, Any]:
    items = await run_in_threadpool(service.list_history, limit)
    return {"count": len(items), "items": items}


@router.get("/studies/{study_id}")
async def study_detail(
    study_id: str,
    service: RadiologyService = Depends(get_radiology_service),
) -> dict[str, Any]:
    return await run_in_threadpool(service.get, study_id)


@router.get("/studies/{study_id}/report")
async def study_report(
    study_id: str,
    service: RadiologyService = Depends(get_radiology_service),
) -> dict[str, Any]:
    return await run_in_threadpool(service.get_report, study_id)
