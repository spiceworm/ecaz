from http import HTTPStatus

from application.constants import messages


def test_bad_login(client):
    resp = client.post(
        "/login",
        follow_redirects=True,
        data={"email": "bad@test.com", "password": "invalid-password"},
    )
    assert len(resp.history) == 0
    assert resp.request.path == "/login"


def test_login(client, user):
    u = user()
    resp = client.post(
        "/login",
        follow_redirects=True,
        data={"email": u.email, "password": u.password},
    )
    assert len(resp.history) == 1
    assert resp.request.path == "/profile"


def test_login_if_already_authenticated(ui_user):
    user = ui_user()
    resp = user.post(
        "/login",
        follow_redirects=True,
        data={"email": user.email, "password": user.password},
    )
    assert len(resp.history) == 1
    assert resp.request.path == "/profile"


def test_login_with_bad_next_url_param(client, user):
    u = user()
    resp = client.post(
        "/login?next=%2Fdoes_not_exist",
        follow_redirects=True,
        data={"email": u.email, "password": u.password},
    )
    assert len(resp.history) == 1
    assert resp.status_code == int(HTTPStatus.NOT_FOUND)


def test_login_with_delete_pending(client, user):
    u = user()
    u.is_deleted = True
    resp = client.post(
        "/login",
        follow_redirects=True,
        data={"email": u.email, "password": u.password},
    )
    assert messages.DELETE_ACCOUNT_PENDING in resp.data.decode()


def test_login_with_next_url_param(client, user):
    u = user()
    resp = client.post(
        "/login?next=%2Fapi_settings",
        follow_redirects=True,
        data={"email": u.email, "password": u.password},
    )
    assert len(resp.history) == 1
    assert resp.request.path == "/api_settings"


def test_bad_login_with_next_url_preserves_next_params(client):
    resp = client.post(
        "/login?next=%2Fapi_settings",
        follow_redirects=True,
        data={"email": "invalid@test.com", "password": "invalid123"},
    )
    assert resp.request.args["next"] == "/api_settings"
