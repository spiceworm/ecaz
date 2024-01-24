def test_logout(ui_user):
    resp = ui_user().post("/logout", follow_redirects=True)
    assert len(resp.history) == 1
    assert resp.request.path == "/"
