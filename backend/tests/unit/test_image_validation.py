from __future__ import annotations

import pytest

from app.core.config import InferenceSettings
from app.utils import image_validation
from app.utils.image_validation import ImageValidationError
from tests.helpers.images import jpeg_bytes, png_bytes


@pytest.fixture
def settings() -> InferenceSettings:
    return InferenceSettings()


class TestExtension:
    def test_empty_filename_raises(self, settings):
        with pytest.raises(ImageValidationError, match="A file is required"):
            image_validation.validate_extension("", settings.allowed_extensions)

    def test_unsupported_extension_raises(self, settings):
        with pytest.raises(ImageValidationError, match="Unsupported"):
            image_validation.validate_extension("a.gif", settings.allowed_extensions)

    def test_accepts_jpg(self, settings):
        assert image_validation.validate_extension("a.jpg", settings.allowed_extensions) == ".jpg"

    def test_accepts_png(self, settings):
        assert image_validation.validate_extension("x.PNG", settings.allowed_extensions) == ".png"


class TestMimeType:
    def test_no_mime_is_allowed(self, settings):
        image_validation.validate_mime_type(None, settings.allowed_mime_types)
        image_validation.validate_mime_type("", settings.allowed_mime_types)

    def test_unsupported_mime_raises(self, settings):
        with pytest.raises(ImageValidationError):
            image_validation.validate_mime_type("application/pdf", settings.allowed_mime_types)


class TestBytes:
    def test_empty_bytes_raises(self, settings):
        with pytest.raises(ImageValidationError, match="Empty"):
            image_validation.validate_image_bytes(b"", ".jpg", settings.max_file_size_bytes)

    def test_oversize_raises(self, settings):
        too_big = b"\x00" * (settings.max_file_size_bytes + 1)
        with pytest.raises(ImageValidationError, match="size limit"):
            image_validation.validate_image_bytes(too_big, ".jpg", settings.max_file_size_bytes)

    def test_non_image_bytes_raises(self, settings):
        with pytest.raises(ImageValidationError, match="Invalid image"):
            image_validation.validate_image_bytes(b"not-an-image", ".jpg", settings.max_file_size_bytes)

    def test_format_extension_mismatch_raises(self, settings):
        # JPEG bytes but tagged with .png extension
        with pytest.raises(ImageValidationError, match="does not match"):
            image_validation.validate_image_bytes(jpeg_bytes(), ".png", settings.max_file_size_bytes)

    def test_valid_jpeg_passes(self, settings):
        image_validation.validate_image_bytes(jpeg_bytes(), ".jpg", settings.max_file_size_bytes)

    def test_valid_png_passes(self, settings):
        image_validation.validate_image_bytes(png_bytes(), ".png", settings.max_file_size_bytes)


class TestValidateAggregate:
    def test_valid_jpeg_end_to_end(self, settings):
        image_validation.validate("scan.jpg", "image/jpeg", jpeg_bytes(), settings)

    def test_valid_png_end_to_end(self, settings):
        image_validation.validate("scan.png", "image/png", png_bytes(), settings)

    def test_pdf_mime_rejected(self, settings):
        with pytest.raises(ImageValidationError):
            image_validation.validate("scan.jpg", "application/pdf", jpeg_bytes(), settings)

    def test_bytes_format_mismatch_with_extension(self, settings):
        # File says .png but bytes are actually JPEG → content vs extension mismatch
        with pytest.raises(ImageValidationError, match="does not match"):
            image_validation.validate("scan.png", "image/png", jpeg_bytes(), settings)
