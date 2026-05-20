from __future__ import annotations

from datetime import datetime, timezone
from typing import Any
from uuid import uuid4

import psycopg

from app.db.session import DatabaseSession
from app.repositories import quality_repository


class QualityEventNotFoundError(LookupError):
    pass


class QualityService:
    def __init__(self, db_session: DatabaseSession):
        self._db = db_session

    def record(
        self,
        cursor: psycopg.Cursor,
        *,
        source: str,
        severity: str,
        event_type: str,
        message: str,
        metadata: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """Insert a quality event using the caller's cursor so it joins the
        ongoing transaction. The orchestrating service decides commit/rollback.
        """
        event_id = str(uuid4())
        created_at = datetime.now(timezone.utc)
        quality_repository.insert(
            cursor,
            event_id=event_id,
            created_at=created_at,
            source=source,
            severity=severity,
            event_type=event_type,
            message=message,
            metadata=metadata or {},
        )
        return {
            "event_id": event_id,
            "created_at": created_at.isoformat(),
            "source": source,
            "severity": severity,
            "event_type": event_type,
            "message": message,
            "metadata": metadata or {},
        }

    def list_recent(self, limit: int) -> list[dict[str, Any]]:
        with self._db.read_cursor() as cursor:
            return quality_repository.list_recent(cursor, limit)

    def resolve(self, event_id: str) -> dict[str, Any]:
        with self._db.transaction() as cursor:
            updated = quality_repository.mark_resolved(cursor, event_id)
        if updated is None:
            raise QualityEventNotFoundError(event_id)
        return updated
