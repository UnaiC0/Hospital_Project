from __future__ import annotations

import json
from datetime import datetime
from typing import Any

import psycopg


INSERT_EVENT = """
INSERT INTO quality_events (
    id, created_at, source, severity, event_type, message, metadata
)
VALUES (%s, %s, %s, %s, %s, %s, %s::jsonb);
"""


SELECT_RECENT = """
SELECT id, created_at, source, severity, event_type, message, metadata, resolved
FROM quality_events
ORDER BY created_at DESC
LIMIT %s;
"""


COUNT_OPEN_BY_SEVERITY = """
SELECT severity, COUNT(*) AS count
FROM quality_events
WHERE resolved = FALSE
GROUP BY severity
ORDER BY severity;
"""


MARK_RESOLVED = """
UPDATE quality_events
SET resolved = TRUE
WHERE id = %s
RETURNING id, created_at, source, severity, event_type, message, metadata, resolved;
"""


def insert(
    cursor: psycopg.Cursor,
    *,
    event_id: str,
    created_at: datetime,
    source: str,
    severity: str,
    event_type: str,
    message: str,
    metadata: dict[str, Any],
) -> None:
    cursor.execute(
        INSERT_EVENT,
        (
            event_id,
            created_at,
            source,
            severity,
            event_type,
            message,
            json.dumps(metadata),
        ),
    )


def list_recent(cursor: psycopg.Cursor, limit: int) -> list[dict[str, Any]]:
    cursor.execute(SELECT_RECENT, (limit,))
    return [
        {
            "event_id": row["id"],
            "created_at": row["created_at"].isoformat(),
            "source": row["source"],
            "severity": row["severity"],
            "event_type": row["event_type"],
            "message": row["message"],
            "metadata": row["metadata"],
            "resolved": row["resolved"],
        }
        for row in cursor.fetchall()
    ]


def count_open_by_severity(cursor: psycopg.Cursor) -> dict[str, int]:
    cursor.execute(COUNT_OPEN_BY_SEVERITY)
    return {row["severity"]: row["count"] for row in cursor.fetchall()}


def mark_resolved(cursor: psycopg.Cursor, event_id: str) -> dict[str, Any] | None:
    cursor.execute(MARK_RESOLVED, (event_id,))
    row = cursor.fetchone()
    if not row:
        return None
    return {
        "event_id": row["id"],
        "created_at": row["created_at"].isoformat(),
        "source": row["source"],
        "severity": row["severity"],
        "event_type": row["event_type"],
        "message": row["message"],
        "metadata": row["metadata"],
        "resolved": row["resolved"],
    }
