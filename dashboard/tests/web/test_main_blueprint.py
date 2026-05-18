from __future__ import annotations

import io

import pytest

from app.services.backend_client import BackendError
from app.services.storage_client import StorageError
from tests.helpers.images import jpeg_bytes, png_bytes

pytestmark = pytest.mark.web


def _prediction_payload(**overrides):
    payload = {
        "class": "Sana",
        "probabilities": {"Sana": 0.8, "Neumonia": 0.15, "COVID-19": 0.05},
        "confidence": 0.8,
        "study_id": "s-1",
        "created_at": "2026-05-14T10:00:00+00:00",
        "quality_status": "accepted",
        "storage": {"report_object_key": "radiology-reports/s-1.json"},
        "quality_flags": [],
        "events": [],
    }
    payload.update(overrides)
    return payload


class TestIndex:
    def test_index_renders_when_authenticated(self, authenticated_client):
        response = authenticated_client.get("/")
        assert response.status_code == 200
        assert b"<html" in response.data.lower() or b"<!doctype" in response.data.lower()


class TestUpload:
    def test_happy_path(self, authenticated_client, fake_backend, fake_storage):
        fake_backend.predict_response = _prediction_payload()
        response = authenticated_client.post(
            "/upload",
            data={"file": (io.BytesIO(jpeg_bytes()), "scan.jpg")},
            content_type="multipart/form-data",
        )
        assert response.status_code == 200
        assert len(fake_storage.uploaded) == 1
        assert len(fake_backend.predict_calls) == 1
        assert fake_backend.predict_calls[0]["source_object_key"] == fake_storage.next_object_key

    def test_png_path(self, authenticated_client, fake_backend):
        fake_backend.predict_response = _prediction_payload()
        response = authenticated_client.post(
            "/upload",
            data={"file": (io.BytesIO(png_bytes()), "scan.png")},
            content_type="multipart/form-data",
        )
        assert response.status_code == 200

    def test_invalid_extension_returns_400(self, authenticated_client):
        response = authenticated_client.post(
            "/upload",
            data={"file": (io.BytesIO(b"abc"), "scan.gif")},
            content_type="multipart/form-data",
        )
        assert response.status_code == 400

    def test_non_image_returns_400(self, authenticated_client):
        response = authenticated_client.post(
            "/upload",
            data={"file": (io.BytesIO(b"not-an-image"), "scan.jpg")},
            content_type="multipart/form-data",
        )
        assert response.status_code == 400

    def test_extension_mismatch_returns_400(self, authenticated_client):
        response = authenticated_client.post(
            "/upload",
            data={"file": (io.BytesIO(jpeg_bytes()), "scan.png")},
            content_type="multipart/form-data",
        )
        assert response.status_code == 400

    def test_backend_failure_returns_502(self, authenticated_client, fake_backend):
        fake_backend.predict_error = BackendError("backend down")
        response = authenticated_client.post(
            "/upload",
            data={"file": (io.BytesIO(jpeg_bytes()), "scan.jpg")},
            content_type="multipart/form-data",
        )
        assert response.status_code == 502

    def test_storage_failure_returns_502(self, authenticated_client, fake_storage):
        fake_storage.upload_error = StorageError("minio down")
        response = authenticated_client.post(
            "/upload",
            data={"file": (io.BytesIO(jpeg_bytes()), "scan.jpg")},
            content_type="multipart/form-data",
        )
        assert response.status_code == 502


class TestProtectedRoutes:
    def test_upload_without_login_redirects(self, client):
        response = client.post(
            "/upload",
            data={"file": (io.BytesIO(jpeg_bytes()), "scan.jpg")},
            content_type="multipart/form-data",
            follow_redirects=False,
        )
        assert response.status_code == 302
        assert "/login" in response.headers["Location"]
