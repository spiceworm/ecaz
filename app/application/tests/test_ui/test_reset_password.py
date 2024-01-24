from datetime import timedelta
import time

from application.constants import messages
from application.models import (
    ApiToken,
)


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


def test_reset_password_using_invalid_email_link(client, user):
    token = ApiToken.create(user(), "not-password-reset-token")
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
