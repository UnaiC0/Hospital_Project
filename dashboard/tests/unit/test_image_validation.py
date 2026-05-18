from __future__ import annotations

from io import BytesIO

import pytest

from app.core.config import UploadSettings
from app.validation.image import ValidationError, validate_upload
from tests.helpers.images import jpeg_bytes, png_bytes


class FakeFileStorage:
    def __init__(self, filename: str, body: bytes):
        self.filename = filename
        self._body = body

    def read(self) -> bytes:
        return self._body


@pytest.fixture
def settings() -> UploadSettings:
    return UploadSettings()


def test_none_file_rejected(settings):
    with pytest.raises(ValidationError, match="seleccionar"):
        validate_upload(None, settings)


def test_empty_filename_rejected(settings):
    with pytest.raises(ValidationError):
        validate_upload(FakeFileStorage("", jpeg_bytes()), settings)


def test_extension_missing_rejected(settings):
    with pytest.raises(ValidationError, match="extension"):
        validate_upload(FakeFileStorage("scan", jpeg_bytes()), settings)


def test_unsupported_extension_rejected(settings):
    with pytest.raises(ValidationError, match="Formato"):
        validate_upload(FakeFileStorage("scan.gif", jpeg_bytes()), settings)


def test_empty_body_rejected(settings):
    with pytest.raises(ValidationError, match="vacio"):
        validate_upload(FakeFileStorage("scan.jpg", b""), settings)


def test_oversize_rejected(settings):
    huge = b"\x00" * (settings.max_file_size_bytes + 1)
    with pytest.raises(ValidationError, match="maximo"):
        validate_upload(FakeFileStorage("scan.jpg", huge), settings)


def test_non_image_rejected(settings):
    with pytest.raises(ValidationError, match="no es una imagen"):
        validate_upload(FakeFileStorage("scan.jpg", b"not-an-image-at-all"), settings)


def test_format_extension_mismatch_rejected(settings):
    with pytest.raises(ValidationError, match="no coincide"):
        validate_upload(FakeFileStorage("scan.png", jpeg_bytes()), settings)


def test_valid_jpeg_accepted(settings):
    validated = validate_upload(FakeFileStorage("Scan.JPG", jpeg_bytes()), settings)
    assert validated.extension == "jpg"
    assert validated.mime_type == "image/jpeg"


def test_valid_png_accepted(settings):
    validated = validate_upload(FakeFileStorage("scan.png", png_bytes()), settings)
    assert validated.extension == "png"
    assert validated.mime_type == "image/png"
