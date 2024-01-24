from http import HTTPStatus

from application.models import (
    db,
    User,
)


def test_change_password(ui_auth_post):
    resp1 = ui_auth_post(
        "/change_password",
        follow_redirects=True,
        data={
            "password1": "new-password",
            "password2": "new-password",
        },
    )
    assert "Password updated" in resp1.data.decode()
    resp2 = ui_auth_post(
        "/change_password",
        follow_redirects=True,
        data={
            "password1": "test-password",
            "password2": "test-password",
        },
    )
    assert "Password updated" in resp2.data.decode()


def test_change_password_not_matching(ui_auth_post):
    resp = ui_auth_post(
        "/change_password",
        follow_redirects=True,
        data={
            "password1": "new-password",
            "password2": "this-does-not-match",
        },
    )
    assert "Passwords must match" in resp.data.decode()


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
        data={"email": user.email, "password": "test-password"},
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


def test_login_with_next_url_param(client, user):
    resp = client.post(
        "/login?next=%2Fapi_settings",
        follow_redirects=True,
        data={"email": user.email, "password": "test-password"},
    )
    assert len(resp.history) == 1
    assert resp.request.path == "/api_settings"


def test_login_with_bad_next_url_param(client, user):
    resp = client.post(
        "/login?next=%2Fdoes_not_exist",
        follow_redirects=True,
        data={"email": user.email, "password": "test-password"},
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


def test_logout(ui_auth_post):
    resp = ui_auth_post("/logout", follow_redirects=True)
    assert len(resp.history) == 1
    print(resp.request.path)
    assert resp.request.path in ("/", "/login")


def test_profile(ui_auth_get):
    resp = ui_auth_get("/profile")
    assert resp.request.path == "/profile"


def test_register(client):
    resp = client.post(
        "/register",
        follow_redirects=True,
        data={"email": "u@test.com", "password": "password123"},
    )
    user = User.query.filter_by(email="u@test.com")
    assert user
    assert len(resp.history) == 1
    assert resp.request.path == "/profile"
    user.delete()
    db.session.commit()


def test_register_duplicate_email(client):
    client.post(
        "/register",
        follow_redirects=True,
        data={"email": "u@test.com", "password": "password123"},
    )
    client.post("/logout")

    resp = client.post(
        "/register",
        follow_redirects=True,
        data={"email": "u@test.com", "password": "password456"},
    )
    assert "Email already taken" in resp.data.decode()
    db.session.rollback()

    User.query.filter_by(email="u@test.com").delete()
    db.session.commit()
