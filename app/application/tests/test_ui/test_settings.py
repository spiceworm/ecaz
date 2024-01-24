from datetime import timedelta

from application.constants import messages
from application.models import ApiToken


def test_change_password(ui_user):
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


def test_send_verify_email(ui_user):
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
    resp = ui_user(is_verified=True).post(
        "/settings/verify",
        follow_redirects=True,
    )
    assert messages.ACCOUNT_ALREADY_VERIFIED in resp.data.decode()


def test_verify_account(ui_user):
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
