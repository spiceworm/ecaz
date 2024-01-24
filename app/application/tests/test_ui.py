from application.models import (
    db,
    User,
)


def test_create_api_token(ui_auth_post, user):
    token_name = "test-token-1"
    assert len(user.api_tokens) == 0
    ui_auth_post("/create_api_token", data={"token_name": token_name})
    assert len(user.api_tokens) == 1
    assert user.api_tokens[0].name == token_name


def test_delete_api_token(ui_auth_post, user):
    token_name = "test-token-1"
    assert len(user.api_tokens) == 0
    ui_auth_post("/create_api_token", data={"token_name": token_name})
    assert len(user.api_tokens) == 1
    ui_auth_post("/delete_api_token", data={"id": user.api_tokens[0].id})
    assert len(user.api_tokens) == 0


def test_login(client, user):
    resp = client.post(
        "/login",
        follow_redirects=True,
        data={"username": user.username, "password": "test-password"},
    )
    assert len(resp.history) == 1
    assert resp.request.path == "/profile"


def test_bad_login(client):
    resp = client.post(
        "/login",
        follow_redirects=True,
        data={"username": "invalid-username", "password": "invalid-password"},
    )
    assert len(resp.history) == 0
    assert resp.request.path == "/login"


def test_logout(ui_auth_post):
    resp = ui_auth_post("/logout", follow_redirects=True)
    assert len(resp.history) == 1
    assert resp.request.path == "/login"


def test_profile(ui_auth_get):
    resp = ui_auth_get("/profile")
    assert resp.request.path == "/profile"


def test_register(client):
    resp = client.post(
        "/register",
        follow_redirects=True,
        data={"username": "u", "password": "p"},
    )
    user = User.query.filter_by(username="u")
    assert user
    assert len(resp.history) == 1
    assert resp.request.path == "/profile"
    user.delete()
    db.session.commit()


def test_register_duplicate_username(client):
    client.post(
        "/register",
        follow_redirects=True,
        data={"username": "u", "password": "p"},
    )
    client.post("/logout")

    resp = client.post(
        "/register",
        follow_redirects=True,
        data={"username": "u", "password": "p"},
    )
    assert "Username already taken" in resp.data.decode()
    db.session.rollback()

    User.query.filter_by(username="u").delete()
    db.session.commit()
