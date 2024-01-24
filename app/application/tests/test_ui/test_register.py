from application.constants import messages
from application.models import (
    db,
    User,
)


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
