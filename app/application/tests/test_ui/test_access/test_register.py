from application.constants import messages
from application.models import (
    db,
    User,
)


def test_register(client):
    """
    Verify form submission to /register with valid values creates a `User` entry
    and redirects the user to their profile page.
    """
    resp = client.post(
        "/register",
        follow_redirects=True,
        data={"email": "user@test.com", "password": "password123"},
    )
    user = User.query.filter_by(email="user@test.com")
    assert user
    assert len(resp.history) == 1
    assert resp.request.path == "/profile"


def test_register_attempt_if_authenticated(ui_user):
    """
    Verify an authenticated user trying to access /register is redirected to their
    profile page.
    """
    resp = ui_user().get(
        "/register",
        follow_redirects=True,
    )
    assert len(resp.history) == 1
    assert resp.request.path == "/profile"


def test_register_duplicate_email(client, user):
    """
    Verify that the correct error message is shown if a user tries to register
    using an email address that is already in use by another user.
    """
    u = user()
    resp = client.post(
        "/register",
        follow_redirects=True,
        data={"email": u.email, "password": "some-password"},
    )
    assert messages.DUPLICATE_EMAIL_ERROR in resp.data.decode()
    db.session.rollback()
