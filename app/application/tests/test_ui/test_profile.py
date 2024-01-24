def test_profile(ui_user):
    resp = ui_user().get("/profile")
    assert resp.request.path == "/profile"
