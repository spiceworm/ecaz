from http import HTTPStatus


def test_bad_login(client):
    resp = client.post(
        "/login",
        follow_redirects=True,
        data={"email": "bad@test.com", "password": "invalid-password"},
    )
    assert len(resp.history) == 0
    assert resp.request.path == "/login"


def test_login(ui_user):
    user = ui_user()
    resp = user.post(
        "/login",
        follow_redirects=True,
        data={"email": user.email, "password": user.password},
    )
    assert len(resp.history) == 1
    assert resp.request.path == "/profile"


def test_login_with_bad_next_url_param(client, ui_user):
    user = ui_user()
    resp = client.post(
        "/login?next=%2Fdoes_not_exist",
        follow_redirects=True,
        data={"email": user.email, "password": user.password},
    )
    assert len(resp.history) == 1
    assert resp.status_code == int(HTTPStatus.NOT_FOUND)


def test_login_with_next_url_param(client, ui_user):
    user = ui_user()
    resp = client.post(
        "/login?next=%2Fapi_settings",
        follow_redirects=True,
        data={"email": user.email, "password": user.password},
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
