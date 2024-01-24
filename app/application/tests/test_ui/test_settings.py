from datetime import timedelta

from application.constants import messages
from application.models import (
    ApiToken,
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
        "/settings/change_password",
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
        "/settings/change_password",
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
        "/settings/change_username",
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
        "/settings/change_username",
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
    resp = user.post("/settings/delete_account", follow_redirects=True)
    assert messages.DELETE_ACCOUNT_SUCCESS in resp.data.decode()
    assert User.query.filter_by(email=user.email).one_or_none() is None
    assert len(resp.history) == 1
    assert resp.request.path == "/"


def test_delete_account_cascades(api_token, ui_user):
    """
    Verify delete account form submission on settings page deletes all `ApiTokens`
    associated with the user.
    """
    user = ui_user()
    t1 = api_token(user=user, name="t1")
    t2 = api_token(user=user, name="t2")
    t3 = api_token(user=user, name="t3")
    assert len(user.api_tokens) == 3
    user.post("/settings/delete_account")
    assert User.query.filter_by(email=user.email).one_or_none() is None
    assert ApiToken.query.filter_by(name=t1.name).one_or_none() is None
    assert ApiToken.query.filter_by(name=t2.name).one_or_none() is None
    assert ApiToken.query.filter_by(name=t3.name).one_or_none() is None


def test_send_verify_email(ui_user):
    """
    Verify that when a user clicks the verify button next to their email address
    on the settings page that it creates an `ApiToken` instance with the
    `ApiToken.VERIFY_EMAIL_TAG` and shows a notification telling the user that
    a verification email has been sent.
    """
    user = ui_user()
    assert len(user.api_tokens) == 0
    resp = user.post(
        "/settings/verify",
        follow_redirects=True,
    )
    assert len(resp.history) == 1
    assert resp.request.path == "/settings"
    assert messages.VERIFICATION_EMAIL_SENT in resp.data.decode()
    assert len(user.api_tokens) == 1
    assert user.api_tokens[0].tags == [ApiToken.HIDDEN_TAG, ApiToken.VERIFY_EMAIL_TAG]


def test_send_verify_email_if_already_verified(ui_user):
    """
    Verify that if a user tries to send a POST to /settings/verify, and they have
    already verified their email, that the appropriate notification is shown.
    """
    resp = ui_user(is_verified=True).post(
        "/settings/verify",
        follow_redirects=True,
    )
    assert messages.ACCOUNT_ALREADY_VERIFIED in resp.data.decode()


def test_verify_account(ui_user):
    """
    Test happy happy path for when a user clicks the unique link emailed to them
    to verify their email address.
    """
    user = ui_user()
    assert not user.is_verified
    token = ApiToken.create_email_verification_token(user)
    resp = user.get(
        f"/settings/verify/{token.value}",
        follow_redirects=True,
    )
    assert user.is_verified
    assert messages.ACCOUNT_VERIFIED_SUCCESS in resp.data.decode()


def test_verify_account_using_expired_token(ui_user):
    """
    Verify that the correct error message is shown if the user clicks the link
    emailed to them to verify their email address but the token in the link
    has expired.
    """
    user = ui_user()
    token = ApiToken.create(
        user,
        ApiToken.RESET_PASSWORD_TAG,
        [ApiToken.HIDDEN_TAG, ApiToken.RESET_PASSWORD_TAG],
        expires_delta=timedelta(microseconds=1),
    )
    resp = user.get(
        f"/settings/verify/{token.value}",
        follow_redirects=True,
    )
    assert not user.is_verified
    assert messages.INVALID_TOKEN in resp.data.decode()
