from flask import url_for

from application.constants import messages
from application.models import AuthToken


def test_forgot_password_when_authenticated(ui_user):
    """
    Verify an authenticated user navigating to /forgot_password is redirected to
    their settings page.
    """
    resp = ui_user().get(
        url_for("ui_bp.forgot_password"),
        follow_redirects=True,
    )
    assert len(resp.history) == 1
    assert resp.request.base_url == url_for("ui_bp.profile")


def test_forgot_password_when_unauthenticated(client, user):
    """
    Verify an unauthenticated user navigating to /forgot_password can submit the
    form and generate an AuthToken used for password resets.
    """
    u = user(email="user@test.com", password="old-password", is_verified=True)
    assert len(u.auth_tokens) == 0
    resp = client.post(
        url_for("ui_bp.forgot_password"),
        follow_redirects=True,
        data={"email": u.email},
    )
    assert len(u.auth_tokens) == 1
    assert u.auth_tokens[0].tags == [AuthToken.HIDDEN_TAG, AuthToken.RESET_PASSWORD_TAG]
    assert messages.PASSWORD_RESET_EMAIL_SENT in resp.data.decode()


def test_forgot_password_when_unauthenticated_using_unverified_email(client, user):
    """
    Verify an unauthenticated user navigating to /forgot_password can submit the
    form and generate an AuthToken used for password resets.
    """
    u = user(email="user@test.com", password="old-password", is_verified=False)
    assert len(u.auth_tokens) == 0
    resp = client.post(
        url_for("ui_bp.forgot_password"),
        follow_redirects=True,
        data={"email": u.email},
    )
    assert len(u.auth_tokens) == 0
    assert messages.USER_NOT_FOUND_OR_EMAIL_NOT_VERIFIED in resp.data.decode()
