from __future__ import annotations

from flask import Blueprint, current_app, render_template, request
from werkzeug.exceptions import RequestEntityTooLarge

from app.auth.session import require_login
from app.core.logging import get_logger
from app.presenters.page import PageInputs, PagePresenter
from app.presenters.prediction import build_image_preview, format_file_size, normalize_backend_prediction
from app.services.backend_client import BackendClient, BackendError
from app.services.storage_client import StorageClient, StorageError
from app.validation.image import ValidationError, validate_upload


bp = Blueprint("main", __name__)
logger = get_logger(__name__)


def _presenter() -> PagePresenter:
    return current_app.config["PAGE_PRESENTER"]


def _backend() -> BackendClient:
    return current_app.config["BACKEND_CLIENT"]


def _storage() -> StorageClient:
    return current_app.config["STORAGE_CLIENT"]


@bp.get("/")
@require_login
def index():
    context = _presenter().build_context(PageInputs())
    return render_template("index.html", **context)


@bp.post("/upload")
@require_login
def upload():
    image_preview = None
    uploaded_filename = None
    uploaded_size = None
    upload_settings = current_app.config["UPLOAD_SETTINGS"]

    try:
        validated = validate_upload(request.files.get("file"), upload_settings)
        uploaded_filename = validated.original_name
        uploaded_size = format_file_size(validated.file_bytes)
        image_preview = build_image_preview(validated.file_bytes, validated.mime_type)

        object_key = _storage().upload_image(
            file_bytes=validated.file_bytes,
            extension=validated.extension,
            mime_type=validated.mime_type,
        )
        backend_payload = _backend().request_prediction(
            file_bytes=validated.file_bytes,
            filename=validated.original_name,
            mime_type=validated.mime_type,
            source_object_key=object_key,
        )
        prediction = normalize_backend_prediction(backend_payload)

        context = _presenter().build_context(
            PageInputs(
                success="Imagen procesada correctamente.",
                image_preview=image_preview,
                prediction_class=prediction["class"],
                probabilities=prediction["probabilities"],
                object_key=object_key,
                uploaded_filename=uploaded_filename,
                uploaded_size=uploaded_size,
                study_id=prediction.get("study_id"),
                report_object_key=prediction.get("storage", {}).get("report_object_key"),
            )
        )
        return render_template("index.html", **context)

    except ValidationError as exc:
        return _render_error(str(exc), 400, image_preview, uploaded_filename, uploaded_size)
    except (BackendError, StorageError) as exc:
        logger.warning("upload_external_dependency_failed", extra={"error": str(exc)})
        return _render_error(str(exc), 502, image_preview, uploaded_filename, uploaded_size)
    except ValueError as exc:
        return _render_error(str(exc), 502, image_preview, uploaded_filename, uploaded_size)
    except Exception:
        logger.exception("upload_unexpected_failure")
        return _render_error(
            "Se produjo un error interno al procesar la solicitud.",
            500,
            image_preview,
            uploaded_filename,
            uploaded_size,
        )


def _render_error(message, status_code, image_preview, filename, size):
    context = _presenter().build_context(
        PageInputs(
            error=message,
            image_preview=image_preview,
            uploaded_filename=filename,
            uploaded_size=size,
        )
    )
    return render_template("index.html", **context), status_code


@bp.app_errorhandler(RequestEntityTooLarge)
def handle_large_file(_error):
    context = _presenter().build_context(
        PageInputs(error="El archivo supera el tamano maximo de 5 MB.")
    )
    return render_template("index.html", **context), 413
