from http import HTTPStatus

from application.constants import messages


def test_bad_login(client):
    """
    Verify a form submission to /login with bad credentials produces the correct
    error message.
    """
    resp = client.post(
        "/login",
        follow_redirects=True,
        data={"email": "bad@test.com", "password": "invalid-password"},
    )
    assert len(resp.history) == 0
    assert resp.request.path == "/login"


def test_login(client, user):
    """
    Verify a form submission to /login with valid credentials redirects the user
    to their profile page.
    """
    u = user()
    resp = client.post(
        "/login",
        follow_redirects=True,
        data={"email": u.email, "password": u.password},
    )
    assert len(resp.history) == 1
    assert resp.request.path == "/profile"


def test_login_if_already_authenticated(ui_user):
    """
    Verify an authenticated user who navigates to /login is redirected to their
    profile page.
    """
    user = ui_user()
    resp = user.post(
        "/login",
        follow_redirects=True,
        data={"email": user.email, "password": user.password},
    )
    assert len(resp.history) == 1
    assert resp.request.path == "/profile"


def test_login_with_bad_next_url_param(client, user):
    """
    Verify an unauthenticated user who tries to navigate to a route requiring
    authentication is prompted to login before being told the page does not
    exist.
    """
    u = user()
    resp = client.post(
        "/login?next=%2Fdoes_not_exist",
        follow_redirects=True,
        data={"email": u.email, "password": u.password},
    )
    assert len(resp.history) == 1
    assert resp.status_code == int(HTTPStatus.NOT_FOUND)


def test_login_with_delete_pending(client, user):
    """
    Verify a user whose account is marked for deletion is shown the appropriate
    notification when they try to login.
    """
    u = user()
    u.is_deleted = True
    resp = client.post(
        "/login",
        follow_redirects=True,
        data={"email": u.email, "password": u.password},
    )
    assert messages.DELETE_ACCOUNT_PENDING in resp.data.decode()


def test_login_with_next_url_param(client, user):
    """
    Verify an unauthenticated user who tries to navigate to a route requiring
    authentication is prompted to login before being redirected to the page
    they were initially trying to access.
    """
    u = user()
    resp = client.post(
        "/login?next=%2Fapi_settings",
        follow_redirects=True,
        data={"email": u.email, "password": u.password},
    )
    assert len(resp.history) == 1
    assert resp.request.path == "/api_settings"


def test_bad_login_with_next_url_preserves_next_params(client):
    """
    Verify that when an unauthenticated user tries to navigate to a route requiring
    authentication, and they provide invalid credentials, the page they were initially
    trying to access is preserved in the URL.
    """
    resp = client.post(
        "/login?next=%2Fapi_settings",
        follow_redirects=True,
        data={"email": "invalid@test.com", "password": "invalid123"},
    )
    assert resp.request.args["next"] == "/api_settings"
