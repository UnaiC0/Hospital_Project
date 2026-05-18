from __future__ import annotations

from typing import Any

from pydantic import BaseModel


class QualityEvent(BaseModel):
    event_id: str
    created_at: str
    source: str
    severity: str
    event_type: str
    message: str
    metadata: dict[str, Any]
    resolved: bool


class QualityEventsResponse(BaseModel):
    count: int
    items: list[QualityEvent]
