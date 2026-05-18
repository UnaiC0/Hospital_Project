from __future__ import annotations

from flask import Blueprint, current_app, redirect, render_template, request, session, url_for

from app.auth.service import AuthService
from app.auth.session import login_user, logout_user


bp = Blueprint("auth", __name__)


def _service() -> AuthService:
    return current_app.config["AUTH_SERVICE"]


@bp.get("/login")
def login_page():
    if "username" in session:
        return redirect(url_for("main.index"))
    return render_template("login.html", error=request.args.get("error"))


@bp.post("/login")
def login_submit():
    username = request.form.get("username", "").strip()
    password = request.form.get("password", "")
    user = _service().authenticate(username, password)
    if user is None:
        return redirect(url_for("auth.login_page", error="Usuario o contraseña incorrectos."))
    login_user(user)
    return redirect(url_for("main.index"))


@bp.get("/logout")
def logout():
    logout_user()
    return redirect(url_for("auth.login_page"))
