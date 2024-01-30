from flask import url_for


def test_admin_access(ui_user):
    """
    Verify happy path for an admin user who is accessing /admin/ view.
    """
    user = ui_user(is_admin=True)
    assert user.is_admin
    resp = user.get(url_for("admin.index"))
    assert resp.request.base_url == url_for("admin.index")


def test_admin_access_when_not_authenticated(client):
    """
    Verify unauthenticated user accessing /admin/ is redirected to login page.
    """
    resp = client.get(
        url_for("admin.index"),
        follow_redirects=True,
    )
    assert len(resp.history) == 1
    assert resp.request.base_url == url_for("ui_bp.login")


def test_admin_access_as_non_admin(ui_user):
    """
    Verify authenticated non-admin user accessing /admin/ is redirected to their
    profile page.
    """
    user = ui_user()
    assert not user.is_admin
    resp = user.get(
        url_for("admin.index"),
        follow_redirects=True,
    )
    assert len(resp.history) == 2
    assert resp.request.base_url == url_for("ui_bp.profile")
