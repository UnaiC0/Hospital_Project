from __future__ import annotations

from dataclasses import dataclass

from werkzeug.security import check_password_hash

from app.core.config import UserCredentials


@dataclass(frozen=True)
class AuthenticatedUser:
    username: str
    role: str
    display_name: str


class AuthService:
    """Verifies credentials against the in-memory user table loaded from env."""

    def __init__(self, users: tuple[UserCredentials, ...]):
        self._by_username = {user.username: user for user in users}

    def authenticate(self, username: str, password: str) -> AuthenticatedUser | None:
        user = self._by_username.get(username)
        if not user:
            return None
        if not check_password_hash(user.password_hash, password):
            return None
        return AuthenticatedUser(
            username=user.username,
            role=user.role,
            display_name=user.display_name,
        )
