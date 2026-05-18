from __future__ import annotations

from typing import Any

from fastapi import APIRouter, Depends, Query
from fastapi.concurrency import run_in_threadpool

from app.api.deps import get_quality_service
from app.schemas.quality import QualityEvent, QualityEventsResponse
from app.services.quality_service import QualityService

router = APIRouter(tags=["quality"])


@router.get("/quality/events", response_model=QualityEventsResponse)
async def quality_events(
    limit: int = Query(default=10, ge=1, le=100),
    service: QualityService = Depends(get_quality_service),
) -> dict[str, Any]:
    items = await run_in_threadpool(service.list_recent, limit)
    return {"count": len(items), "items": items}


@router.patch("/quality/events/{event_id}/resolve", response_model=QualityEvent)
async def resolve_event(
    event_id: str,
    service: QualityService = Depends(get_quality_service),
) -> dict[str, Any]:
    return await run_in_threadpool(service.resolve, event_id)
