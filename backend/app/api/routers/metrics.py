from __future__ import annotations

from typing import Any

from fastapi import APIRouter, Depends
from fastapi.concurrency import run_in_threadpool

from app.api.deps import get_metrics_service
from app.schemas.metrics import PlatformMetrics
from app.services.metrics_service import MetricsService

router = APIRouter(tags=["metrics"])


@router.get("/metrics", response_model=PlatformMetrics)
async def metrics(service: MetricsService = Depends(get_metrics_service)) -> dict[str, Any]:
    return await run_in_threadpool(service.platform_snapshot)
