def test_logout(ui_user):
    """
    Verify form submission to /logout.
    """
    resp = ui_user().post("/logout", follow_redirects=True)
    assert len(resp.history) == 1
    assert resp.request.path == "/"
