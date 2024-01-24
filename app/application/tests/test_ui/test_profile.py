def test_profile(ui_user):
    """
    Verify navigating to /profile works.
    """
    resp = ui_user().get("/profile")
    assert resp.request.path == "/profile"
