from flask import url_for

from application.constants import messages


def test_generate_random_username(client, monkeypatch):
    """
    Verify GET to /api/v1/generate-username.
    """
    username = "username"
    monkeypatch.setattr("application.api.v1.misc.generate_unique_username", lambda: username)
    resp = client.get(url_for("api_misc_bp.generateusernameapi"))
    assert resp.json["username"] == username


def test_status_endpoint(client):
    """
    Verify GET to /api/v1/status.
    """
    resp = client.get(url_for("api_misc_bp.statusapi"))
    assert resp.json == {"message": "ok"}


class TestTerminalApi:
    endpoint = "api_misc_bp.terminalapi"

    def test_as_admin(self, api_user):
        """
        Verify admins are able to successfully use the terminal api endpoint.
        """
        user = api_user(is_admin=True)
        assert user.is_admin
        resp = user.post(url_for(self.endpoint), json={"command": "whoami"})
        assert resp.json == {"output": "root"}

    def test_as_admin_using_invalid_command(self, api_user):
        """
        Verify exceptions are properly handled when thrown from invalid commands.
        """
        user = api_user(is_admin=True)
        assert user.is_admin
        resp = user.post(url_for(self.endpoint), json={"command": "invalid command"})
        assert "No such file or directory" in resp.json["output"]

    def test_as_not_admin(self, api_user):
        """
        Verify only admins are able to use the terminal api endpoint.
        """
        user = api_user()
        assert not user.is_admin
        resp = user.post(url_for(self.endpoint), json={"command": "whoami"})
        assert resp.json == {"output": messages.RESTRICTED_TO_ADMIN}
