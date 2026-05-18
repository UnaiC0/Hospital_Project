from __future__ import annotations

import os
from io import BytesIO

from PIL import Image, UnidentifiedImageError

from app.core.config import InferenceSettings


PREDICT_FORMAT_EXTENSIONS = {
    "JPEG": {".jpg", ".jpeg"},
    "PNG": {".png"},
}


class ImageValidationError(ValueError):
    pass


def validate_extension(filename: str, allowed_extensions: frozenset[str]) -> str:
    name = (filename or "").strip()
    if not name:
        raise ImageValidationError("A file is required")
    extension = os.path.splitext(name)[1].lower()
    if extension not in allowed_extensions:
        raise ImageValidationError("Unsupported file type")
    return extension


def validate_mime_type(content_type: str | None, allowed_mime_types: frozenset[str]) -> None:
    if not content_type:
        return
    if content_type.lower() not in allowed_mime_types:
        raise ImageValidationError("Unsupported file type")


def validate_image_bytes(image_bytes: bytes, extension: str, max_size_bytes: int) -> None:
    if not image_bytes:
        raise ImageValidationError("Empty file")
    if len(image_bytes) > max_size_bytes:
        raise ImageValidationError("File exceeds the size limit")

    try:
        with Image.open(BytesIO(image_bytes)) as image:
            image.verify()
        with Image.open(BytesIO(image_bytes)) as image:
            detected_format = (image.format or "").upper()
    except (UnidentifiedImageError, OSError, ValueError) as exc:
        raise ImageValidationError("Invalid image file") from exc

    allowed_for_format = PREDICT_FORMAT_EXTENSIONS.get(detected_format)
    if not allowed_for_format:
        raise ImageValidationError("Unsupported image format")
    if extension not in allowed_for_format:
        raise ImageValidationError("File extension does not match the image content")


def validate(
    filename: str,
    content_type: str | None,
    image_bytes: bytes,
    settings: InferenceSettings,
) -> None:
    extension = validate_extension(filename, settings.allowed_extensions)
    validate_mime_type(content_type, settings.allowed_mime_types)
    validate_image_bytes(image_bytes, extension, settings.max_file_size_bytes)
