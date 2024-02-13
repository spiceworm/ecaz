import http

from flask import url_for

from application.constants import messages
from application.models import AuthToken


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


class TestVerifyEmailApi:
    endpoint = "api_misc_bp.verifyemailapi"

    def test_if_not_verified(self, api_user):
        """
        Test happy path for where a user clicks the "Verify" button to send a verification email.
        """
        user = api_user()
        assert len(user.auth_tokens) == 1
        resp = user.post(url_for(self.endpoint))
        assert resp.json == messages.VERIFICATION_EMAIL_SENT
        assert resp.status_code == http.HTTPStatus.OK
        assert len(user.auth_tokens) == 2
        assert user.auth_tokens[-1].tags == [AuthToken.HIDDEN_TAG, AuthToken.VERIFY_EMAIL_TAG]

    def test_if_already_verified(self, api_user):
        """
        Test scenario for if a request is sent to send the verification email for a user whose
        email is already verified.
        """
        user = api_user(is_verified=True)
        assert len(user.auth_tokens) == 1
        resp = user.post(url_for(self.endpoint))
        assert resp.json == messages.ACCOUNT_ALREADY_VERIFIED
        assert resp.status_code == http.HTTPStatus.OK
        assert len(user.auth_tokens) == 1

    def test_if_email_verified_by_different_user(self, api_user):
        """
        Test scenario for when a user has set their email to one that is already verified by a
        different account and tries to verify it under their own account.
        """
        user1 = api_user(email="same@test.com", is_verified=True)
        user2 = api_user(email="same@test.com")
        assert len(user2.auth_tokens) == 1
        resp = user2.post(url_for(self.endpoint))
        assert resp.json == messages.EMAIL_VERIFIED_BY_DIFFERENT_ACCOUNT_ERROR
        assert resp.status_code == http.HTTPStatus.CONFLICT
        assert len(user2.auth_tokens) == 1

    def test_as_invalid_user(self, bad_auth_token_api_user):
        """
        Test scenario for when a valid JWT is used for the request but that token does not
        correspond to any user.
        """
        user = bad_auth_token_api_user()
        resp = user.post(url_for(self.endpoint))
        assert resp.status_code == http.HTTPStatus.UNAUTHORIZED
