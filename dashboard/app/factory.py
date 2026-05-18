from __future__ import annotations

from pathlib import Path

from flask import Flask

from app.auth.service import AuthService
from app.auth.session import current_user
from app.blueprints import auth as auth_bp
from app.blueprints import main as main_bp
from app.core.config import Settings, get_settings
from app.core.logging import configure_logging
from app.presenters.page import PagePresenter
from app.services.backend_client import BackendClient
from app.services.dashboard_data import DashboardDataService
from app.services.storage_client import StorageClient


PROJECT_ROOT = Path(__file__).resolve().parents[1]
TEMPLATES_DIR = PROJECT_ROOT / "templates"
STATIC_DIR = PROJECT_ROOT / "static"


def create_app(settings: Settings | None = None) -> Flask:
    configure_logging()
    if settings is None:
        settings = get_settings()

    app = Flask(
        __name__,
        template_folder=str(TEMPLATES_DIR),
        static_folder=str(STATIC_DIR),
    )
    app.config["MAX_CONTENT_LENGTH"] = settings.upload.max_file_size_bytes
    app.config["SESSION_COOKIE_HTTPONLY"] = True
    app.config["SESSION_COOKIE_SAMESITE"] = "Lax"
    app.config["SESSION_COOKIE_SECURE"] = settings.session.cookie_secure
    app.secret_key = settings.session.secret_key

    backend_client = BackendClient(settings.backend)
    storage_client = StorageClient(settings.object_storage)
    auth_service = AuthService(settings.users)
    page_presenter = PagePresenter(
        storage_settings=settings.object_storage,
        data_service=DashboardDataService(backend_client),
    )

    app.config["BACKEND_CLIENT"] = backend_client
    app.config["STORAGE_CLIENT"] = storage_client
    app.config["AUTH_SERVICE"] = auth_service
    app.config["PAGE_PRESENTER"] = page_presenter
    app.config["UPLOAD_SETTINGS"] = settings.upload

    @app.context_processor
    def inject_user():
        return {"current_user": current_user()}

    app.register_blueprint(auth_bp.bp)
    app.register_blueprint(main_bp.bp)

    return app
