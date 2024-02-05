from flask import url_for


def test_view_saved(ui_user):
    user = ui_user()
    url = url_for("ui_bp.view_saved")
    resp = user.get(url)
    assert resp.request.base_url == url
