from __future__ import annotations

from io import BytesIO

from PIL import Image


def jpeg_bytes(size: tuple[int, int] = (64, 64), color: tuple[int, int, int] = (180, 180, 180)) -> bytes:
    buf = BytesIO()
    Image.new("RGB", size, color).save(buf, format="JPEG")
    return buf.getvalue()


def png_bytes(size: tuple[int, int] = (64, 64), color: tuple[int, int, int] = (180, 180, 180)) -> bytes:
    buf = BytesIO()
    Image.new("RGB", size, color).save(buf, format="PNG")
    return buf.getvalue()
