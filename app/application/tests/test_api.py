def test_status_endpoint(api_get):
    resp = api_get("/api/v1/status")
    assert resp.json == {"message": "ok"}


def test_user_endpoint(api_auth_get, user):
    resp = api_auth_get("/api/v1/user")
    assert resp.json == {"logged_in_as": user.username}
