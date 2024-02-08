import flask
from flask import url_for


from application.constants import messages
from application.models import (
    db,
    User,
)


class TestRegister:
    def test_valid(self, client):
        """
        Verify form submission to /register with valid values creates a `User` entry
        and redirects the user to their profile page.
        """
        resp = client.post(
            url_for("ui_bp.register"),
            follow_redirects=True,
            data={"email": "user@test.com", "password": "password123"},
        )
        user = User.query.filter_by(email="user@test.com")
        assert user
        assert len(resp.history) == 1
        assert resp.request.base_url == url_for("ui_bp.profile")

    def test_if_already_authenticated(self, ui_user):
        """
        Verify an authenticated user trying to access /register is redirected to their
        profile page.
        """
        resp = ui_user().get(
            url_for("ui_bp.register"),
            follow_redirects=True,
        )
        assert len(resp.history) == 1
        assert resp.request.base_url == url_for("ui_bp.profile")

    def test_if_registration_disabled(self, client, monkeypatch):
        """
        Verify the appropriate message is shown and that registration attempts do
        not succeed if the environment variable REGISTRATION_ENABLED=False.
        """
        updated_config = {**flask.current_app.config, **{"REGISTRATION_ENABLED": False}}
        monkeypatch.setattr(flask.current_app, "config", updated_config)

        resp1 = client.get(url_for("ui_bp.register"))
        assert messages.REGISTRATION_DISABLED in resp1.data.decode()

        resp2 = client.post(
            url_for("ui_bp.register"),
            data={"email": "user@test.com", "password": "password123"},
        )
        assert messages.REGISTRATION_DISABLED in resp2.data.decode()
        assert User.query.count() == 0
