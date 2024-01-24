from datetime import timedelta
import time

from application.constants import messages
from application.models import (
    ApiToken,
)


def test_reset_password_submit_new_password(client, user):
    """
    Verify that when a user clicks the link emailed to them containing a unique
    URL for resetting their password, and they submit the form on /reset_password,
    that it does reset their password and redirect them to the login page.
    """
    u = user()
    token = ApiToken.create_reset_password_token(u)
    new_password = "new-password"
    resp = client.post(
        f"/reset_password/{token.value}",
        follow_redirects=True,
        data={"password1": new_password, "password2": new_password},
    )
    assert u.password == new_password
    assert messages.PASSWORD_UPDATE_SUCCESS in resp.data.decode()
    assert len(resp.history) == 1
    assert resp.request.path == "/"


def test_reset_password_submit_non_matching_passwords(client, user):
    """
    Verify that when a user clicks the link emailed to them containing a unique
    URL for resetting their password, and they submit the form on /reset_password
    using password values that do not match, they are shown the correct error
    message, stay on the same page, and their original password remains unchanged.
    """
    u = user()
    old_password = u.password
    token = ApiToken.create_reset_password_token(u)
    resp = client.post(
        f"/reset_password/{token.value}",
        follow_redirects=True,
        data={"password1": "new-password", "password2": "does-not-match"},
    )
    assert u.password == old_password
    assert messages.PASSWORD_UPDATE_MATCH_ERROR in resp.data.decode()
    assert resp.request.path == f"/reset_password/{token.value}"


def test_reset_password_using_expired_token(client, user):
    """
    Verify that when a user clicks the link emailed to them containing a unique
    URL for resetting their password, but the token in the link has expired, that
    they are shown the correct error message and redirected back to /forgot_password
    page to have a new link emailed to them.
    """
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
    """
    Verify that when a user clicks the link emailed to them containing a unique
    URL for resetting their password, that they are redirected back to the
    /forgot_password page if the token in the link is not valid.
    """
    token = ApiToken.create(user(), "not-password-reset-token")
    resp = client.get(
        f"/reset_password/{token.value}",
        follow_redirects=True,
    )
    assert messages.INVALID_TOKEN in resp.data.decode()
    assert len(resp.history) == 1
    assert resp.request.path == "/forgot_password"


def test_reset_password_using_valid_email_link(client, user):
    """
    Verify that when a user clicks the link emailed to them containing a unique
    URL for resetting their password, it takes them to the page containing the
    password reset form.
    """
    token = ApiToken.create_reset_password_token(user())
    resp = client.get(f"/reset_password/{token.value}")
    assert resp.request.path == f"/reset_password/{token.value}"
