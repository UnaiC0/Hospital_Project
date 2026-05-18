from __future__ import annotations

from contextlib import contextmanager
from datetime import datetime, timezone
from typing import Any


class FakeCursor:
    """In-memory cursor double. Records every execute() call and serves
    pre-loaded fetchone/fetchall responses one by one."""

    def __init__(self) -> None:
        self.executed: list[tuple[str, Any]] = []
        self._fetchone_queue: list[dict[str, Any] | None] = []
        self._fetchall_queue: list[list[dict[str, Any]]] = []

    # ---- test setup helpers ----
    def queue_one(self, row: dict[str, Any] | None) -> None:
        self._fetchone_queue.append(row)

    def queue_all(self, rows: list[dict[str, Any]]) -> None:
        self._fetchall_queue.append(rows)

    # ---- psycopg cursor interface ----
    def execute(self, sql: str, params: Any = None) -> None:
        self.executed.append((sql, params))

    def fetchone(self) -> dict[str, Any] | None:
        if not self._fetchone_queue:
            return None
        return self._fetchone_queue.pop(0)

    def fetchall(self) -> list[dict[str, Any]]:
        if not self._fetchall_queue:
            return []
        return self._fetchall_queue.pop(0)

    def __enter__(self) -> "FakeCursor":
        return self

    def __exit__(self, *args: Any) -> None:
        return None


class FakeDatabaseSession:
    """Substitutes app.db.session.DatabaseSession.
    Exposes the same context manager protocol but never touches Postgres."""

    def __init__(self) -> None:
        self.cursor = FakeCursor()
        self.transaction_count = 0
        self.read_count = 0

    @contextmanager
    def transaction(self):
        self.transaction_count += 1
        yield self.cursor

    @contextmanager
    def read_cursor(self):
        self.read_count += 1
        yield self.cursor


class FakeObjectStorage:
    """In-memory object storage. Substitutes ObjectStorage transparently."""

    bucket = "test-bucket"

    def __init__(self) -> None:
        self.objects: dict[str, tuple[Any, str]] = {}
        self.ensure_bucket_calls = 0
        self.fail_on_get: bool = False

    def ensure_bucket(self) -> None:
        self.ensure_bucket_calls += 1

    def put_bytes(self, object_key: str, body: bytes, content_type: str) -> None:
        self.objects[object_key] = (body, content_type)

    def put_json(self, object_key: str, document: dict[str, Any]) -> None:
        self.objects[object_key] = (document, "application/json")

    def get_json(self, object_key: str) -> dict[str, Any]:
        if self.fail_on_get:
            raise RuntimeError("storage get failed")
        if object_key not in self.objects:
            raise KeyError(object_key)
        return self.objects[object_key][0]


class StubInferenceService:
    """Deterministic inference double. Tests configure the response."""

    model_name = "stub-inference"
    model_version = "0.0.1"
    model_family = "stub"

    def __init__(self, response: dict[str, Any] | None = None) -> None:
        self._response = response or self._default_response()

    @staticmethod
    def _default_response() -> dict[str, Any]:
        return {
            "model_name": "stub-inference",
            "model_version": "0.0.1",
            "model_family": "stub",
            "class": "Sana",
            "probabilities": {"Sana": 0.8, "Neumonia": 0.15, "COVID-19": 0.05},
            "confidence": 0.8,
            "features": {"mean_intensity": 180.0, "contrast": 40.0, "input_size_bytes": 1024},
            "preprocessing": {"color_space": "grayscale", "resize": [256, 256], "normalization": "stub"},
            "quality_flags": [],
            "explanation": "stub",
            "clinical_note": "stub",
        }

    def predict(self, image_bytes: bytes) -> dict[str, Any]:
        return dict(self._response)


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


def row_with_timestamps(row: dict[str, Any]) -> dict[str, Any]:
    """Ensure timestamp columns are datetime instances so .isoformat() works."""
    if "created_at" in row and isinstance(row["created_at"], str):
        row["created_at"] = datetime.fromisoformat(row["created_at"])
    if "last_study_at" in row and isinstance(row["last_study_at"], str):
        row["last_study_at"] = datetime.fromisoformat(row["last_study_at"])
    if "finished_at" in row and isinstance(row["finished_at"], str):
        row["finished_at"] = datetime.fromisoformat(row["finished_at"])
    return row
