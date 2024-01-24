def test_status_endpoint(client):
    resp = client.get("/api/v1/status")
    assert resp.json == {"message": "ok"}


def test_user_endpoint(api_user):
    user = api_user()
    resp = user.get("/api/v1/user")
    assert resp.json == {"logged_in_as": user.email}
