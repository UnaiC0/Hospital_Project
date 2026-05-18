from __future__ import annotations

from werkzeug.security import generate_password_hash

from app.auth.service import AuthService, AuthenticatedUser
from app.core.config import UserCredentials


def make_users():
    return (
        UserCredentials(
            username="admin",
            password_hash=generate_password_hash("AdminPass", method="pbkdf2:sha256:1000000"),
            role="admin",
            display_name="Administrador",
        ),
        UserCredentials(
            username="doctor",
            password_hash=generate_password_hash("DoctorPass", method="pbkdf2:sha256:1000000"),
            role="user",
            display_name="Doctor",
        ),
    )


def test_correct_credentials_return_user():
    service = AuthService(make_users())
    user = service.authenticate("admin", "AdminPass")
    assert isinstance(user, AuthenticatedUser)
    assert user.role == "admin"
    assert user.display_name == "Administrador"


def test_wrong_password_returns_none():
    service = AuthService(make_users())
    assert service.authenticate("admin", "nope") is None


def test_unknown_user_returns_none():
    service = AuthService(make_users())
    assert service.authenticate("ghost", "AdminPass") is None
