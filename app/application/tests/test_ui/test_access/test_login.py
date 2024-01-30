from http import HTTPStatus

from flask import url_for
import pytest

from application.constants import messages
from application.models import AuthToken


def test_bad_login(client):
    """
    Verify a form submission to /login with bad credentials produces the correct
    error message.
    """
    resp = client.post(
        url_for("ui_bp.login"),
        follow_redirects=True,
        data={"email": "bad@test.com", "password": "invalid-password"},
    )
    assert len(resp.history) == 0
    assert resp.request.base_url == url_for("ui_bp.login")


def test_login(client, user):
    """
    Verify a form submission to /login with valid credentials redirects the user
    to their profile page.
    """
    u = user()
    resp = client.post(
        url_for("ui_bp.login"),
        follow_redirects=True,
        data={"email": u.email, "password": u.password},
    )
    assert len(resp.history) == 1
    assert resp.request.base_url == url_for("ui_bp.profile")


def test_login_if_already_authenticated(ui_user):
    """
    Verify an authenticated user who navigates to /login is redirected to their
    profile page.
    """
    user = ui_user()
    resp = user.post(
        url_for("ui_bp.login"),
        follow_redirects=True,
        data={"email": user.email, "password": user.password},
    )
    assert len(resp.history) == 1
    assert resp.request.base_url == url_for("ui_bp.profile")


def test_login_with_bad_next_url_param(client, user):
    """
    Verify an unauthenticated user who tries to navigate to a route requiring
    authentication is prompted to login before being told the page does not
    exist.
    """
    u = user()
    resp = client.post(
        url_for("ui_bp.login", next="does-not-exist"),
        follow_redirects=True,
        data={"email": u.email, "password": u.password},
    )
    assert len(resp.history) == 1
    assert resp.json == {"error": HTTPStatus.NOT_FOUND.phrase}


def test_login_with_delete_account_pending(client, user):
    """
    Verify a user whose account is marked for deletion is shown the appropriate
    notification when they try to login.
    """
    u = user()
    u.is_deleted = True
    resp = client.post(
        url_for("ui_bp.login"),
        follow_redirects=True,
        data={"email": u.email, "password": u.password},
    )
    assert messages.DELETE_ACCOUNT_PENDING in resp.data.decode()


def test_login_with_mfa_where_webauthn_supercedes_totp(client, user):
    """
    Verify that if a user has both totp and webauthn mfa enabled for their
    account that webauthn is used as it is a more secure form of mfa.
    """
    u = user()
    u.mfa.totp.enabled = True
    u.mfa.webauthn.enabled = True
    resp = client.post(
        url_for("ui_bp.login"),
        follow_redirects=True,
        data={"email": u.email, "password": u.password},
    )
    token = [t for t in u.auth_tokens if t.WEBAUTHN_MFA_TAG in t.tags][0]
    assert len(resp.history) == 1
    assert resp.request.base_url == url_for("ui_bp.webauthn_login", jwt=token.value)


def test_login_with_valid_next_url_param(client, user):
    """
    Verify an unauthenticated user who tries to navigate to a route requiring
    authentication is prompted to login before being redirected to the page
    they were initially trying to access.
    """
    u = user()
    resp = client.post(
        "/login?next=%2Fsettings%2Fauth_token",
        follow_redirects=True,
        data={"email": u.email, "password": u.password},
    )
    assert len(resp.history) == 1
    assert resp.request.base_url == url_for("ui_bp.auth_token_settings")


def test_bad_login_with_next_url_preserves_next_params(client):
    """
    Verify that when an unauthenticated user tries to navigate to a route requiring
    authentication, and they provide invalid credentials, the page they were initially
    trying to access is preserved in the URL.
    """
    next_arg = "settings/auth_token"
    resp = client.post(
        url_for("ui_bp.login", next="settings/auth_token"),
        follow_redirects=True,
        data={"email": "invalid@test.com", "password": "invalid123"},
    )
    assert resp.request.args["next"] == next_arg


def test_login_with_totp_mfa_enabled(client, user):
    """
    Verify a form submission to /login with valid credentials redirects the user
    to the Totp login page. Verify submitting a valid code to the Totp login page
    redirects the user to their profile.
    """
    u = user()
    u.mfa.totp.enabled = True
    resp1 = client.post(
        url_for("ui_bp.login"),
        follow_redirects=True,
        data={"email": u.email, "password": u.password},
    )
    token = u.auth_tokens[0]
    totp_login_url = url_for("ui_bp.totp_login", jwt=token.value)

    assert AuthToken.TOTP_MFA_TAG in token.tags
    assert len(resp1.history) == 1
    assert resp1.request.base_url == totp_login_url

    resp2 = client.post(
        totp_login_url,
        follow_redirects=True,
        data={"totp_code": u.mfa.totp.handler.now()},
    )
    assert len(resp2.history) == 1
    assert resp2.request.base_url == url_for("ui_bp.profile")


def test_login_with_invalid_totp_code(client, user):
    """
    Verify a form submission to /login with valid credentials redirects the user
    to the Totp login page. Verify submitting an invalid code to the Totp login page
    displays the correct error message.
    """
    u = user()
    u.mfa.totp.enabled = True
    resp1 = client.post(
        url_for("ui_bp.login"),
        follow_redirects=True,
        data={"email": u.email, "password": u.password},
    )
    token = u.auth_tokens[0]
    totp_login_url = url_for("ui_bp.totp_login", jwt=token.value)

    assert AuthToken.TOTP_MFA_TAG in token.tags
    assert len(resp1.history) == 1
    assert resp1.request.base_url == totp_login_url

    resp2 = client.post(
        totp_login_url,
        follow_redirects=True,
        data={"totp_code": int(u.mfa.totp.handler.now()) + 1},
    )
    assert messages.TOTP_CODE_INVALID in resp2.data.decode()
    assert len(resp2.history) == 0
    assert resp2.request.base_url == totp_login_url


@pytest.mark.parametrize("mfa_type", ["totp", "webauthn"])
def test_access_mfa_login_page_if_already_authenticated(ui_user, mfa_type):
    """
    Verify navigating to the mfa login pages when the user is already authenticated
    redirects them to their profile.
    """
    user = ui_user()
    getattr(user.mfa, mfa_type).enabled = True
    token = getattr(AuthToken, f"create_mfa_{mfa_type}_token")(user)
    resp = user.get(
        f"/login/mfa/{mfa_type}/{token.value}",
        follow_redirects=True,
    )
    assert len(resp.history) == 1
    assert resp.request.base_url == url_for("ui_bp.profile")


@pytest.mark.parametrize("mfa_type", ["totp", "webauthn"])
def test_access_mfa_login_page_with_invalid_jwt_in_url(client, user, mfa_type):
    """
    Verify navigating to the mfa login pages when url contains a JWT that is not specific
    the MFA action being attempted redirects the user to the login page.
    """
    u = user()
    getattr(u.mfa, mfa_type).enabled = True
    token = AuthToken.create_email_verification_token(u)
    resp = client.get(
        f"/login/mfa/{mfa_type}/{token.value}",
        follow_redirects=True,
    )
    assert len(resp.history) == 1
    assert resp.request.base_url == url_for("ui_bp.login")
