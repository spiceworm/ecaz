from flask import url_for


def test_profile(ui_user):
    """
    Verify navigating to /profile works.
    """
    resp = ui_user().get(url_for("ui_bp.profile"))
    assert resp.request.base_url == url_for("ui_bp.profile")
