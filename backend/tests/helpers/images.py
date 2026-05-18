from __future__ import annotations

from io import BytesIO

from PIL import Image


def jpeg_bytes(size: tuple[int, int] = (64, 64), color: tuple[int, int, int] = (180, 180, 180)) -> bytes:
    buffer = BytesIO()
    Image.new("RGB", size, color).save(buffer, format="JPEG")
    return buffer.getvalue()


def png_bytes(size: tuple[int, int] = (64, 64), color: tuple[int, int, int] = (180, 180, 180)) -> bytes:
    buffer = BytesIO()
    Image.new("RGB", size, color).save(buffer, format="PNG")
    return buffer.getvalue()


def dark_jpeg_bytes() -> bytes:
    return jpeg_bytes(color=(10, 10, 10))


def bright_jpeg_bytes() -> bytes:
    return jpeg_bytes(color=(245, 245, 245))


def low_contrast_png_bytes() -> bytes:
    return png_bytes(color=(128, 128, 128))
