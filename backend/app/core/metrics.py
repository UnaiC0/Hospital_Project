from __future__ import annotations

import time

from fastapi import FastAPI, Request
from prometheus_client import CONTENT_TYPE_LATEST, CollectorRegistry, Counter, Histogram, generate_latest


REGISTRY = CollectorRegistry()

HTTP_REQUESTS_TOTAL = Counter(
    "hospital_http_requests_total",
    "Total HTTP requests handled by the backend.",
    labelnames=("method", "path", "status"),
    registry=REGISTRY,
)

HTTP_REQUEST_DURATION_SECONDS = Histogram(
    "hospital_http_request_duration_seconds",
    "HTTP request latency in seconds.",
    labelnames=("method", "path"),
    registry=REGISTRY,
    buckets=(0.01, 0.05, 0.1, 0.25, 0.5, 1.0, 2.5, 5.0, 10.0),
)

RADIOLOGY_PREDICTIONS_TOTAL = Counter(
    "hospital_radiology_predictions_total",
    "Radiology predictions emitted, partitioned by class.",
    labelnames=("class_label",),
    registry=REGISTRY,
)

TRIAGE_ASSESSMENTS_TOTAL = Counter(
    "hospital_triage_assessments_total",
    "Triage assessments emitted, partitioned by risk level.",
    labelnames=("risk_level",),
    registry=REGISTRY,
)

QUALITY_EVENTS_RECORDED_TOTAL = Counter(
    "hospital_quality_events_total",
    "Quality events recorded, partitioned by severity.",
    labelnames=("severity",),
    registry=REGISTRY,
)


def register_metrics_middleware(app: FastAPI) -> None:
    """Records request count and latency for every HTTP call. Route templates
    are used as label values so cardinality stays bounded."""

    @app.middleware("http")
    async def _metrics_middleware(request: Request, call_next):
        start = time.perf_counter()
        response = await call_next(request)
        duration = time.perf_counter() - start
        path = _route_path(request)
        HTTP_REQUESTS_TOTAL.labels(
            method=request.method,
            path=path,
            status=str(response.status_code),
        ).inc()
        HTTP_REQUEST_DURATION_SECONDS.labels(method=request.method, path=path).observe(duration)
        return response


def _route_path(request: Request) -> str:
    route = request.scope.get("route")
    if route is not None and getattr(route, "path", None):
        return route.path
    return request.url.path


def render_metrics() -> tuple[bytes, str]:
    return generate_latest(REGISTRY), CONTENT_TYPE_LATEST
