from datetime import timedelta

from application.constants import messages
from application.models import (
    AuthToken,
    User,
)


def test_change_password(ui_user):
    """
    Verify behavior for submitting the form to change the password on the
    settings page.
    """
    user = ui_user()
    password = "new-password"
    resp1 = user.post(
        "/settings/user/password",
        follow_redirects=True,
        data={
            "password1": password,
            "password2": password,
        },
    )
    assert user.password == password
    assert messages.PASSWORD_UPDATE_SUCCESS in resp1.data.decode()


def test_change_password_not_matching(ui_user):
    """
    Verify behavior for submitting the form to change the password on the
    settings page when the password fields do not match.
    """
    user = ui_user()
    old_password = user.password
    resp = user.post(
        "/settings/user/password",
        follow_redirects=True,
        data={
            "password1": "new-password",
            "password2": "this-does-not-match",
        },
    )
    assert user.password == old_password
    assert messages.PASSWORD_UPDATE_MATCH_ERROR in resp.data.decode()


def test_change_username(ui_user):
    """
    Verify behavior for submitting the form to change the username on the
    settings page.
    """
    user = ui_user()
    new_username = "new-username"
    assert user.username != new_username
    resp1 = user.post(
        "/settings/user/username",
        follow_redirects=True,
        data={"username": new_username},
    )
    assert user.username == new_username
    assert messages.USERNAME_UPDATE_SUCCESS in resp1.data.decode()


def test_change_username_to_duplicate(ui_user):
    """
    Verify behavior for submitting the form to change the username on the
    settings page when the username a user is trying to change to is already
    in use by another user.
    """
    duplicate_username = "username"
    ui_user(email="user1@test.com", password="password1", username=duplicate_username)

    user = ui_user(email="user2@test.com", password="password2")
    old_username = user.email
    resp = user.post(
        "/settings/user/username",
        follow_redirects=True,
        data={"username": duplicate_username},
    )
    assert user.username == old_username
    assert messages.DUPLICATE_USERNAME_ERROR in resp.data.decode()


def test_delete_account(ui_user):
    """
    Verify delete account form submission on settings page shows the correct notification
    and deletes the user.
    """
    user = ui_user()
    resp = user.post("/settings/account/delete", follow_redirects=True)
    assert messages.DELETE_ACCOUNT_SUCCESS in resp.data.decode()
    assert User.query.filter_by(email=user.email).one_or_none() is None
    assert len(resp.history) == 1
    assert resp.request.path == "/"


def test_delete_account_cascades(ui_user):
    """
    Verify delete account form submission on settings page deletes all `AuthToken`
    associated with the user.
    """
    user = ui_user()
    t1 = AuthToken.create(user=user, name="t1")
    t2 = AuthToken.create(user=user, name="t2")
    t3 = AuthToken.create(user=user, name="t3")
    assert len(user.auth_tokens) == 3
    user.post("/settings/account/delete")
    assert User.query.filter_by(email=user.email).one_or_none() is None
    assert AuthToken.query.filter_by(name=t1.name).one_or_none() is None
    assert AuthToken.query.filter_by(name=t2.name).one_or_none() is None
    assert AuthToken.query.filter_by(name=t3.name).one_or_none() is None


def test_disable_totp_when_disabled(ui_user):
    """
    Verify the correct error message is shown if a user attempts to disable TOTP
    MFA when it is not enabled for that user.
    """
    user = ui_user()
    resp = user.post(
        "/settings/mfa/totp/disable",
        follow_redirects=True,
    )
    assert messages.TOTP_NOT_ENABLED in resp.data.decode()
    assert len(resp.history) == 1
    assert resp.request.path == "/settings"


def test_disable_totp_when_enabled(ui_user):
    """
    Verify the correct success message is shown if a user successfully disables
    TOTP MFA.
    """
    user = ui_user()
    user.mfa.totp.enabled = True
    resp = user.post(
        "/settings/mfa/totp/disable",
        follow_redirects=True,
    )
    assert messages.TOTP_NOW_DISABLED in resp.data.decode()
    assert len(resp.history) == 1
    assert resp.request.path == "/settings"


def test_disable_webauthn_when_disabled(ui_user):
    """
    Verify the correct error message is shown if a user attempts to disable WebAuthn
    MFA when it is not enabled for that user.
    """
    user = ui_user()
    resp = user.post(
        "/settings/mfa/webauthn/disable",
        follow_redirects=True,
    )
    assert messages.WEBAUTHN_NOT_ENABLED in resp.data.decode()
    assert len(resp.history) == 1
    assert resp.request.path == "/settings"


def test_disable_webauthn_when_enabled(ui_user):
    """
    Verify the correct success message is shown if a user successfully disables
    WebAuthn MFA.
    """
    user = ui_user()
    user.mfa.webauthn.enabled = True
    resp = user.post(
        "/settings/mfa/webauthn/disable",
        follow_redirects=True,
    )
    print(resp.data.decode())
    assert messages.WEBAUTHN_NOW_DISABLED in resp.data.decode()
    assert len(resp.history) == 1
    assert resp.request.path == "/settings"


def test_send_verify_email(ui_user):
    """
    Verify that when a user clicks the verify button next to their email address
    on the settings page that it creates an `AuthToken` instance with the
    `AuthToken.VERIFY_EMAIL_TAG` and shows a notification telling the user that
    a verification email has been sent.
    """
    user = ui_user()
    assert len(user.auth_tokens) == 0
    resp = user.post(
        "/settings/user/email/verify",
        follow_redirects=True,
    )
    assert len(resp.history) == 1
    assert resp.request.path == "/settings"
    assert messages.VERIFICATION_EMAIL_SENT in resp.data.decode()
    assert len(user.auth_tokens) == 1
    assert user.auth_tokens[0].tags == [AuthToken.HIDDEN_TAG, AuthToken.VERIFY_EMAIL_TAG]


def test_send_verify_email_if_already_verified(ui_user):
    """
    Verify that if a user tries to send a POST to /settings/verify, and they have
    already verified their email, that the appropriate notification is shown.
    """
    resp = ui_user(is_verified=True).post(
        "/settings/user/email/verify",
        follow_redirects=True,
    )
    assert messages.ACCOUNT_ALREADY_VERIFIED in resp.data.decode()


def test_verify_email(ui_user):
    """
    Test happy happy path for when a user clicks the unique link emailed to them
    to verify their email address.
    """
    user = ui_user()
    assert not user.is_verified
    token = AuthToken.create_email_verification_token(user)
    resp = user.get(
        f"/settings/user/email/verify/{token.value}",
        follow_redirects=True,
    )
    assert user.is_verified
    assert messages.ACCOUNT_VERIFIED_SUCCESS in resp.data.decode()


def test_verify_email_using_expired_token(ui_user):
    """
    Verify that the correct error message is shown if the user clicks the link
    emailed to them to verify their email address but the token in the link
    has expired.
    """
    user = ui_user()
    token = AuthToken.create_email_verification_token(
        user,
        timedelta(microseconds=1),
    )
    resp = user.get(
        f"/settings/user/email/verify/{token.value}",
        follow_redirects=True,
    )
    assert not user.is_verified
    assert messages.INVALID_TOKEN in resp.data.decode()
