def test_email_endpoint(api_user):
    user = api_user(is_admin=True)
    resp = user.post(
        "/api/v1/email",
        json={
            "subject": "Test",
            "body": "test-email",
            "to": ["user@test.com"],
            "is_html": True,
        }
    )
    assert resp.json == {"status": True}


def test_email_endpoint_failure(api_user, mock_email_send):
    """
    Testing calling the email endpoint as a non-admin user.
    Only admins are allowed to send emails from this endpoint.
    """
    mock_email_send(lambda self: False)
    user = api_user()
    resp = user.post(
        "/api/v1/email",
        json={
            "subject": "Test",
            "body": "test-email",
            "to": ["user@test.com"],
            "is_html": True,
        }
    )
    assert resp.json == {"status": False}


def test_status_endpoint(client):
    resp = client.get("/api/v1/status")
    assert resp.json == {"message": "ok"}


def test_user_endpoint(api_user):
    user = api_user()
    resp = user.get("/api/v1/user")
    assert resp.json == {"logged_in_as": user.email}
