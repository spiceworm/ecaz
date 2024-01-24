from application.constants import messages


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
