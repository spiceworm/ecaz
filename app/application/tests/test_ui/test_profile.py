import pytest

from flask import url_for


@pytest.mark.parametrize(
    "endpoint", [
        "ui_bp.profile",
        "ui_bp.profile_saved",
        "ui_bp.profile_submissions",
        "ui_bp.profile_votes",
    ]
)
def test_profile(ui_user, endpoint):
    """
    Verify navigating to /profile works.
    """
    resp = ui_user().get(url_for(endpoint))
    assert resp.request.base_url == url_for(endpoint)
