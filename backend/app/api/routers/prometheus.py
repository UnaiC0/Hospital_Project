from __future__ import annotations

from fastapi import APIRouter, Response

from app.core.metrics import render_metrics

router = APIRouter(tags=["prometheus"])


@router.get("/metrics/prom", include_in_schema=False)
async def prometheus_metrics() -> Response:
    body, content_type = render_metrics()
    return Response(content=body, media_type=content_type)
