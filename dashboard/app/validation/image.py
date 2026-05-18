from __future__ import annotations

from dataclasses import dataclass
from io import BytesIO

from PIL import Image, UnidentifiedImageError
from werkzeug.utils import secure_filename

from app.core.config import UploadSettings


class ValidationError(Exception):
    pass


ALLOWED_FORMATS: dict[str, dict[str, frozenset[str] | str]] = {
    "JPEG": {"extensions": frozenset({"jpg", "jpeg"}), "mime_type": "image/jpeg"},
    "PNG": {"extensions": frozenset({"png"}), "mime_type": "image/png"},
}


@dataclass(frozen=True)
class ValidatedImage:
    original_name: str
    extension: str
    mime_type: str
    file_bytes: bytes


def validate_upload(file_storage, settings: UploadSettings) -> ValidatedImage:
    if file_storage is None:
        raise ValidationError("Debe seleccionar una imagen.")

    original_name = secure_filename(file_storage.filename or "")
    if not original_name:
        raise ValidationError("El nombre del archivo no es valido.")
    if "." not in original_name:
        raise ValidationError("El archivo debe tener extension.")

    extension = original_name.rsplit(".", 1)[1].lower()
    if extension not in settings.allowed_extensions:
        raise ValidationError("Formato no permitido. Use JPG, JPEG o PNG.")

    file_bytes = file_storage.read()
    if not file_bytes:
        raise ValidationError("El archivo esta vacio.")
    if len(file_bytes) > settings.max_file_size_bytes:
        raise ValidationError("El archivo supera el tamano maximo de 5 MB.")

    try:
        with Image.open(BytesIO(file_bytes)) as image:
            image.verify()
        with Image.open(BytesIO(file_bytes)) as image:
            detected_format = (image.format or "").upper()
    except (UnidentifiedImageError, OSError, ValueError) as exc:
        raise ValidationError("El archivo no es una imagen valida.") from exc

    format_config = ALLOWED_FORMATS.get(detected_format)
    if not format_config:
        raise ValidationError("Formato no permitido. Use JPG, JPEG o PNG.")
    if extension not in format_config["extensions"]:
        raise ValidationError("La extension no coincide con el contenido de la imagen.")

    return ValidatedImage(
        original_name=original_name,
        extension=extension,
        mime_type=str(format_config["mime_type"]),
        file_bytes=file_bytes,
    )
