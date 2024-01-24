def test_email_endpoint(api_user):
    """
    Verify happy path for POST /api/v1/email.
    """
    user = api_user(is_admin=True)
    resp = user.post(
        "/api/v1/email",
        json={
            "subject": "Test",
            "body": "test-email",
            "to": ["user@test.com"],
            "is_html": True,
        },
    )
    assert resp.json == {"status": True}


def test_email_endpoint_failure(api_user, mock_email_send):
    """
    Verify POST to /api/v1/email with non-admin user authentication return False.
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
        },
    )
    assert resp.json == {"status": False}


def test_status_endpoint(client):
    """
    Verify GET to /api/v1/status.
    """
    resp = client.get("/api/v1/status")
    assert resp.json == {"message": "ok"}


def test_user_endpoint(api_user):
    """
    Verify GET to /api/v1/user with user authentication.
    """
    user = api_user()
    resp = user.get("/api/v1/user")
    assert resp.json == {"logged_in_as": user.email}
