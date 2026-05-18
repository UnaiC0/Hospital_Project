from __future__ import annotations

from functools import wraps

from flask import redirect, session, url_for

from app.auth.service import AuthenticatedUser


SESSION_USERNAME_KEY = "username"
SESSION_ROLE_KEY = "role"
SESSION_DISPLAY_KEY = "display_name"


def login_user(user: AuthenticatedUser) -> None:
    session.clear()
    session[SESSION_USERNAME_KEY] = user.username
    session[SESSION_ROLE_KEY] = user.role
    session[SESSION_DISPLAY_KEY] = user.display_name


def logout_user() -> None:
    session.clear()


def current_user() -> AuthenticatedUser | None:
    username = session.get(SESSION_USERNAME_KEY)
    if not username:
        return None
    return AuthenticatedUser(
        username=username,
        role=session.get(SESSION_ROLE_KEY, "user"),
        display_name=session.get(SESSION_DISPLAY_KEY, username),
    )


def require_login(view):
    @wraps(view)
    def wrapper(*args, **kwargs):
        if SESSION_USERNAME_KEY not in session:
            return redirect(url_for("auth.login_page"))
        return view(*args, **kwargs)
    return wrapper
