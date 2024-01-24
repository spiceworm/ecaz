def test_admin_access(ui_user):
    """
    Verify happy path for an admin user who is accessing /admin/ view.
    """
    user = ui_user(is_admin=True)
    assert user.is_admin
    resp = user.get("/admin/")
    assert resp.request.path == "/admin/"


def test_admin_access_when_not_authenticated(client):
    """
    Verify unauthenticated user accessing /admin/ is redirected to login page.
    """
    resp = client.get(
        "/admin/",
        follow_redirects=True,
    )
    assert len(resp.history) == 1
    assert resp.request.path == "/"


def test_admin_access_as_non_admin(ui_user):
    """
    Verify authenticated non-admin user accessing /admin/ is redirected to their
    profile page.
    """
    user = ui_user()
    assert not user.is_admin
    resp = user.get(
        "/admin/",
        follow_redirects=True,
    )
    assert len(resp.history) == 2
    assert resp.request.path == "/profile"
