from __future__ import annotations

import pytest

pytestmark = pytest.mark.web


class TestLoginFlow:
    def test_unauthenticated_root_redirects_to_login(self, client):
        response = client.get("/", follow_redirects=False)
        assert response.status_code == 302
        assert "/login" in response.headers["Location"]

    def test_login_page_renders(self, client):
        response = client.get("/login")
        assert response.status_code == 200
        assert b"<form" in response.data

    def test_authenticated_login_redirects_home(self, client):
        from tests.conftest import KNOWN_ADMIN_PASSWORD
        response = client.post(
            "/login",
            data={"username": "admin", "password": KNOWN_ADMIN_PASSWORD},
            follow_redirects=False,
        )
        assert response.status_code == 302
        assert response.headers["Location"] in {"/", "http://localhost/"}

    def test_wrong_password_redirects_back_with_error(self, client):
        response = client.post(
            "/login",
            data={"username": "admin", "password": "wrong"},
            follow_redirects=False,
        )
        assert response.status_code == 302
        assert "error=" in response.headers["Location"]

    def test_unknown_user_redirects_back_with_error(self, client):
        response = client.post(
            "/login",
            data={"username": "ghost", "password": "x"},
            follow_redirects=False,
        )
        assert "error=" in response.headers["Location"]


class TestLogout:
    def test_logout_clears_session(self, authenticated_client):
        response = authenticated_client.get("/logout", follow_redirects=False)
        assert response.status_code == 302
        # After logout, root should bounce back to /login
        followup = authenticated_client.get("/", follow_redirects=False)
        assert followup.status_code == 302
        assert "/login" in followup.headers["Location"]


class TestSession:
    def test_already_logged_in_visiting_login_redirects_home(self, authenticated_client):
        response = authenticated_client.get("/login", follow_redirects=False)
        assert response.status_code == 302
