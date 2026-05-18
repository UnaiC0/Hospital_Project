"""Dashboard test fixtures.

Sets env vars BEFORE any `from app...` import so get_settings() succeeds.
"""

from __future__ import annotations

import os
import sys
from pathlib import Path

# Make `app` importable when pytest runs from dashboard/ root.
DASHBOARD_ROOT = Path(__file__).resolve().parent.parent
if str(DASHBOARD_ROOT) not in sys.path:
    sys.path.insert(0, str(DASHBOARD_ROOT))

# Werkzeug hash for the password "secret".
_ADMIN_HASH = (
    "pbkdf2:sha256:1000000$abc$"
    "5fb84cd2f0fa362a72e8da92ce72eb38ec3da10ab9e96bd0c8869c3f4cf5a8a4"
)
_USER_HASH = _ADMIN_HASH

os.environ.setdefault("BACKEND_URL", "http://backend.test:8000")
os.environ.setdefault("SECRET_KEY", "test-secret-key")
os.environ.setdefault("SESSION_COOKIE_SECURE", "false")
os.environ.setdefault("ADMIN_USERNAME", "admin")
os.environ.setdefault("ADMIN_PASSWORD_HASH", _ADMIN_HASH)
os.environ.setdefault("USER_USERNAME", "doctor")
os.environ.setdefault("USER_PASSWORD_HASH", _USER_HASH)
os.environ.setdefault("MINIO_ENDPOINT", "http://minio.test:9000")
os.environ.setdefault("MINIO_ACCESS_KEY", "test-access")
os.environ.setdefault("MINIO_SECRET_KEY", "test-secret")
os.environ.setdefault("MINIO_BUCKET_NAME", "test-bucket")
os.environ.setdefault("MINIO_REGION", "us-east-1")
os.environ.setdefault("MINIO_CONSOLE_URL", "http://minio-console.test")

import pytest
from werkzeug.security import generate_password_hash

# Replace the placeholder hashes with real ones bound to a known password
# so the auth tests can sign in.
KNOWN_ADMIN_PASSWORD = "AdminPass123"
KNOWN_USER_PASSWORD = "DoctorPass123"
os.environ["ADMIN_PASSWORD_HASH"] = generate_password_hash(
    KNOWN_ADMIN_PASSWORD, method="pbkdf2:sha256:1000000"
)
os.environ["USER_PASSWORD_HASH"] = generate_password_hash(
    KNOWN_USER_PASSWORD, method="pbkdf2:sha256:1000000"
)

# Reset the lru_cache so the new hashes are picked up.
from app.core import config as config_module
config_module.get_settings.cache_clear()

from app.factory import create_app
from tests.helpers.fakes import FakeBackendClient, FakeStorageClient


@pytest.fixture
def fake_backend():
    return FakeBackendClient()


@pytest.fixture
def fake_storage():
    return FakeStorageClient()


@pytest.fixture
def app(fake_backend, fake_storage):
    from app.core.config import get_settings
    from app.presenters.page import PagePresenter
    from app.services.dashboard_data import DashboardDataService

    application = create_app()
    # Swap real collaborators for in-memory fakes
    application.config["BACKEND_CLIENT"] = fake_backend
    application.config["STORAGE_CLIENT"] = fake_storage
    application.config["PAGE_PRESENTER"] = PagePresenter(
        storage_settings=get_settings().object_storage,
        data_service=DashboardDataService(fake_backend),
    )
    application.config["TESTING"] = True
    return application


@pytest.fixture
def client(app):
    return app.test_client()


@pytest.fixture
def authenticated_client(client):
    client.post("/login", data={"username": "admin", "password": KNOWN_ADMIN_PASSWORD})
    return client
