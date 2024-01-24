from application.constants import messages
from application.models import ApiToken


def test_forgot_password_when_authenticated(ui_user):
    """
    Verify an authenticated user navigating to /forgot_password is redirected to
    their settings page.
    """
    resp = ui_user().get(
        "/forgot_password",
        follow_redirects=True,
    )
    assert len(resp.history) == 1
    assert resp.request.path == "/profile"


def test_forgot_password_when_unauthenticated(client, user):
    """
    Verify an unauthenticated user navigating to /forgot_password can submit the
    form and generate an ApiToken used for password resets.
    """
    u = user("user@test.com", "old-password")
    assert len(u.api_tokens) == 0
    resp = client.post(
        "/forgot_password",
        follow_redirects=True,
        data={"email": u.email},
    )
    assert len(u.api_tokens) == 1
    assert u.api_tokens[0].tags == [ApiToken.HIDDEN_TAG, ApiToken.RESET_PASSWORD_TAG]
    assert messages.PASSWORD_RESET_EMAIL_SENT in resp.data.decode()
