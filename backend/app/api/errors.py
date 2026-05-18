from __future__ import annotations

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from app.core.logging import get_logger
from app.services.quality_service import QualityEventNotFoundError
from app.services.radiology_service import RadiologyStudyNotFoundError
from app.services.triage_service import TriageNotFoundError
from app.storage.object_storage import ObjectStorageError
from app.utils.image_validation import ImageValidationError

logger = get_logger(__name__)


def register_exception_handlers(app: FastAPI) -> None:
    @app.exception_handler(ImageValidationError)
    async def _image_validation(request: Request, exc: ImageValidationError):
        return JSONResponse(status_code=400, content={"detail": str(exc)})

    @app.exception_handler(TriageNotFoundError)
    async def _triage_not_found(request: Request, exc: TriageNotFoundError):
        return JSONResponse(status_code=404, content={"detail": "Triage record not found"})

    @app.exception_handler(RadiologyStudyNotFoundError)
    async def _study_not_found(request: Request, exc: RadiologyStudyNotFoundError):
        return JSONResponse(status_code=404, content={"detail": "Radiology study not found"})

    @app.exception_handler(QualityEventNotFoundError)
    async def _quality_not_found(request: Request, exc: QualityEventNotFoundError):
        return JSONResponse(status_code=404, content={"detail": "Quality event not found"})

    @app.exception_handler(ObjectStorageError)
    async def _storage(request: Request, exc: ObjectStorageError):
        logger.error("object_storage_error", extra={"error": str(exc)})
        return JSONResponse(status_code=502, content={"detail": "Object storage unavailable"})
