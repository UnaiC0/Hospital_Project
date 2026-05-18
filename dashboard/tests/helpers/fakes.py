from __future__ import annotations

from typing import Any

from app.services.backend_client import BackendError


class FakeBackendClient:
    """Stub of BackendClient. Tests set responses; calls are recorded."""

    def __init__(self) -> None:
        self.predict_response: dict[str, Any] | None = None
        self.predict_error: Exception | None = None
        self.get_responses: dict[str, Any] = {}
        self.predict_calls: list[dict[str, Any]] = []

    def request_prediction(self, *, file_bytes, filename, mime_type, source_object_key=None):
        self.predict_calls.append({
            "filename": filename,
            "mime_type": mime_type,
            "source_object_key": source_object_key,
            "size": len(file_bytes),
        })
        if self.predict_error:
            raise self.predict_error
        if self.predict_response is None:
            raise BackendError("no response configured")
        return self.predict_response

    def get(self, path: str, default: Any) -> Any:
        return self.get_responses.get(path, default)


class FakeStorageClient:
    bucket = "test-bucket"

    def __init__(self) -> None:
        self.uploaded: list[dict[str, Any]] = []
        self.upload_error: Exception | None = None
        self.next_object_key: str = "uploads/test-object.jpg"

    def upload_image(self, *, file_bytes, extension, mime_type):
        if self.upload_error:
            raise self.upload_error
        self.uploaded.append({
            "extension": extension,
            "mime_type": mime_type,
            "size": len(file_bytes),
        })
        return self.next_object_key
