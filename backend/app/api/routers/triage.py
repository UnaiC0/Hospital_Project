from __future__ import annotations

from typing import Any

from fastapi import APIRouter, Depends, Query
from fastapi.concurrency import run_in_threadpool

from app.api.deps import get_app_settings, get_triage_service
from app.core.config import Settings
from app.schemas.triage import TriageHistoryResponse, TriageRequest, TriageResponse
from app.services.triage_service import TriageService

router = APIRouter(tags=["triage"])


@router.post("/triage", response_model=TriageResponse)
async def triage(
    payload: TriageRequest,
    service: TriageService = Depends(get_triage_service),
    settings: Settings = Depends(get_app_settings),
) -> dict[str, Any]:
    assessment = service.assess(payload)
    storage_result = await run_in_threadpool(service.register, payload, assessment)
    return {
        "status": "accepted",
        "triage_id": storage_result["triage_id"],
        "created_at": storage_result["created_at"],
        "patient_assessment": assessment,
        "storage": {
            "postgres_database": settings.postgres.database,
            "minio_bucket": storage_result["report_bucket"],
            "minio_object_key": storage_result["report_object_key"],
        },
    }


@router.get("/triage/history", response_model=TriageHistoryResponse)
async def triage_history(
    limit: int = Query(default=10, ge=1, le=100),
    service: TriageService = Depends(get_triage_service),
) -> dict[str, Any]:
    items = await run_in_threadpool(service.list_history, limit)
    return {"count": len(items), "items": items}


@router.get("/triage/{triage_id}")
async def triage_detail(
    triage_id: str,
    service: TriageService = Depends(get_triage_service),
) -> dict[str, Any]:
    return await run_in_threadpool(service.get, triage_id)


@router.get("/triage/{triage_id}/report")
async def triage_report(
    triage_id: str,
    service: TriageService = Depends(get_triage_service),
) -> dict[str, Any]:
    return await run_in_threadpool(service.get_report, triage_id)
