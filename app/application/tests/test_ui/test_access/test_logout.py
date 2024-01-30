from flask import url_for


def test_logout(ui_user):
    """
    Verify form submission to /logout.
    """
    resp = ui_user().post(url_for("ui_bp.logout"), follow_redirects=True)
    assert len(resp.history) == 1
    assert resp.request.base_url == url_for("ui_bp.login")
