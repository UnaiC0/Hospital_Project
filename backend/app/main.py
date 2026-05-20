from __future__ import annotations

from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.api.deps import get_database_session
from app.api.errors import register_exception_handlers
from app.api.routers import health, metrics, quality, radiology, triage
from app.core.config import get_settings
from app.core.logging import configure_logging, get_logger
from app.db.schema import initialize_schema_with_retry


def create_app() -> FastAPI:
    configure_logging()
    settings = get_settings()
    logger = get_logger(__name__)

    @asynccontextmanager
    async def lifespan(_: FastAPI):
        logger.info("startup_begin")
        db_session = get_database_session()
        db_session.open()
        initialize_schema_with_retry(
            db_session,
            attempts=settings.schema_init_attempts,
            delay_seconds=settings.schema_init_delay_seconds,
        )
        logger.info("startup_ready")
        try:
            yield
        finally:
            db_session.close()
            logger.info("shutdown")

    app = FastAPI(title="Hospital Backend", version="3.0.0", lifespan=lifespan)
    register_exception_handlers(app)
    app.include_router(health.router)
    app.include_router(triage.router)
    app.include_router(radiology.router)
    app.include_router(quality.router)
    app.include_router(metrics.router)
    return app


app = create_app()
