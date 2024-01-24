from datetime import timedelta
from http import HTTPStatus
import time

from application.constants import messages
from application.models import (
    ApiToken,
    db,
    User,
)


def test_change_password(ui_user):
    user = ui_user()
    resp1 = user.post(
        "/settings/change_password",
        follow_redirects=True,
        data={
            "password1": "new-password",
            "password2": "new-password",
        },
    )
    assert messages.PASSWORD_UPDATE_SUCCESS in resp1.data.decode()
    resp2 = user.post(
        "/settings/change_password",
        follow_redirects=True,
        data={
            "password1": "test-password",
            "password2": "test-password",
        },
    )
    assert messages.PASSWORD_UPDATE_SUCCESS in resp2.data.decode()


def test_change_password_not_matching(ui_user):
    resp = ui_user().post(
        "/settings/change_password",
        follow_redirects=True,
        data={
            "password1": "new-password",
            "password2": "this-does-not-match",
        },
    )
    assert messages.PASSWORD_UPDATE_MATCH_ERROR in resp.data.decode()


def test_change_username(ui_user):
    resp1 = ui_user().post(
        "/settings/change_username",
        follow_redirects=True,
        data={"username": "new-username"},
    )
    assert messages.USERNAME_UPDATE_SUCCESS in resp1.data.decode()


def test_create_api_token(ui_user):
    user = ui_user()
    token_name = "test-token-1"
    assert len(user.api_tokens) == 0
    user.post("/api_settings/create_api_token", data={"token_name": token_name})
    assert len(user.api_tokens) == 1
    assert user.api_tokens[0].name == token_name


def test_delete_account(ui_user):
    user = ui_user()
    resp = user.post("/settings/delete_account", follow_redirects=True)
    assert messages.DELETE_ACCOUNT_SUCCESS in resp.data.decode()
    assert User.query.filter_by(email=user.email).one_or_none() is None
    assert len(resp.history) == 1
    assert resp.request.path == "/"


def test_delete_account_cascades(ui_user):
    user = ui_user()
    token_name = "test-token"
    user.post("/api_settings/create_api_token", data={"token_name": token_name})
    user.post("/settings/delete_account")
    assert User.query.filter_by(email=user.email).one_or_none() is None
    assert ApiToken.query.filter_by(name=token_name).one_or_none() is None


def test_delete_api_token(ui_user):
    user = ui_user()
    token_name = "test-token-1"
    assert len(user.api_tokens) == 0
    user.post("/api_settings/create_api_token", data={"token_name": token_name})
    assert len(user.api_tokens) == 1
    user.post("/api_settings/delete_api_token", data={"id": user.api_tokens[0].id})
    assert len(user.api_tokens) == 0


def test_login(ui_user):
    user = ui_user()
    resp = user.post(
        "/login",
        follow_redirects=True,
        data={"email": user.email, "password": user.password},
    )
    assert len(resp.history) == 1
    assert resp.request.path == "/profile"


def test_bad_login(client):
    resp = client.post(
        "/login",
        follow_redirects=True,
        data={"email": "bad@test.com", "password": "invalid-password"},
    )
    assert len(resp.history) == 0
    assert resp.request.path == "/login"


def test_forgot_password_when_authenticated(ui_user):
    resp = ui_user().get(
        "/forgot_password",
        follow_redirects=True,
    )
    assert len(resp.history) == 1
    assert resp.request.path == "/profile"


def test_forgot_password_when_unauthenticated(client, user):
    u = user("user@test.com", "old-password")
    resp = client.post(
        "/forgot_password",
        follow_redirects=True,
        data={"email": u.email},
    )
    assert messages.PASSWORD_RESET_EMAIL_SENT in resp.data.decode()


def test_login_with_next_url_param(client, ui_user):
    user = ui_user()
    resp = client.post(
        "/login?next=%2Fapi_settings",
        follow_redirects=True,
        data={"email": user.email, "password": user.password},
    )
    assert len(resp.history) == 1
    assert resp.request.path == "/api_settings"


def test_login_with_bad_next_url_param(client, ui_user):
    user = ui_user()
    resp = client.post(
        "/login?next=%2Fdoes_not_exist",
        follow_redirects=True,
        data={"email": user.email, "password": user.password},
    )
    assert len(resp.history) == 1
    assert resp.status_code == int(HTTPStatus.NOT_FOUND)


def test_bad_login_with_next_url_preserves_next_params(client):
    resp = client.post(
        "/login?next=%2Fapi_settings",
        follow_redirects=True,
        data={"email": "invalid@test.com", "password": "invalid123"},
    )
    assert resp.request.args["next"] == "/api_settings"


def test_logout(ui_user):
    resp = ui_user().post("/logout", follow_redirects=True)
    assert len(resp.history) == 1
    assert resp.request.path == "/"


def test_profile(ui_user):
    resp = ui_user().get("/profile")
    assert resp.request.path == "/profile"


def test_reset_password_using_expired_token(client, user):
    token = ApiToken.create(
        user(),
        ApiToken.RESET_PASSWORD_TAG,
        [ApiToken.HIDDEN_TAG, ApiToken.RESET_PASSWORD_TAG],
        expires_delta=timedelta(microseconds=1),
    )
    time.sleep(0.0000011)
    resp = client.get(
        f"/reset_password/{token.value}",
        follow_redirects=True,
    )
    assert messages.INVALID_TOKEN in resp.data.decode()
    assert len(resp.history) == 1
    assert resp.request.path == "/forgot_password"


def test_reset_password_using_valid_email_link(client, user):
    token = ApiToken.create_reset_password_token(user())
    resp = client.get(f"/reset_password/{token.value}")
    assert resp.request.path == f"/reset_password/{token.value}"


def test_reset_password_using_invalid_email_link(client, user):
    token = ApiToken.create(user(), "not-password-reset-token")
    resp = client.get(
        f"/reset_password/{token.value}",
        follow_redirects=True,
    )
    assert messages.INVALID_TOKEN in resp.data.decode()
    assert len(resp.history) == 1
    assert resp.request.path == "/forgot_password"


def test_reset_password_submit_new_password(client, user):
    token = ApiToken.create_reset_password_token(user())
    resp = client.post(
        f"/reset_password/{token.value}",
        follow_redirects=True,
        data={"password1": "new-password", "password2": "new-password"},
    )
    assert messages.PASSWORD_UPDATE_SUCCESS in resp.data.decode()
    assert len(resp.history) == 1
    assert resp.request.path == "/"


def test_reset_password_submit_non_matching_passwords(client, user):
    token = ApiToken.create_reset_password_token(user())
    resp = client.post(
        f"/reset_password/{token.value}",
        follow_redirects=True,
        data={"password1": "new-password", "password2": "does-not-match"},
    )
    assert messages.PASSWORD_UPDATE_MATCH_ERROR in resp.data.decode()
    assert resp.request.path == f"/reset_password/{token.value}"


def test_register(client):
    resp = client.post(
        "/register",
        follow_redirects=True,
        data={"email": "user@test.com", "password": "password123"},
    )
    user = User.query.filter_by(email="user@test.com")
    assert user
    assert len(resp.history) == 1
    assert resp.request.path == "/profile"


def test_register_duplicate_email(client):
    client.post(
        "/register",
        follow_redirects=True,
        data={"email": "user@test.com", "password": "password123"},
    )
    client.post("/logout")

    resp = client.post(
        "/register",
        follow_redirects=True,
        data={"email": "user@test.com", "password": "password456"},
    )
    assert messages.DUPLICATE_EMAIL_ERROR in resp.data.decode()
    db.session.rollback()
