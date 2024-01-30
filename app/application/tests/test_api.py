from flask import url_for

from application.constants import messages


def test_email_endpoint(api_user):
    """
    Verify happy path for POST /api/v1/email.
    """
    user = api_user(is_admin=True)
    resp = user.post(
        url_for("api_v1_bp.emailapi"),
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
        url_for("api_v1_bp.emailapi"),
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
    resp = client.get(url_for("api_v1_bp.statusapi"))
    assert resp.json == {"message": "ok"}


def test_terminal_api_as_admin(api_user):
    """
    Verify admins are able to successfully use the terminal api endpoint.
    """
    user = api_user(is_admin=True)
    assert user.is_admin
    resp = user.post(
        url_for("api_v1_bp.terminalapi"),
        json={"command": "whoami"},
    )
    assert resp.json == {"output": "root"}


def test_terminal_api_as_admin_using_invalid_command(api_user):
    """
    Verify exceptions are properly handled when thrown from invalid commands.
    """
    user = api_user(is_admin=True)
    assert user.is_admin
    resp = user.post(
        url_for("api_v1_bp.terminalapi"),
        json={"command": "invalid command"},
    )
    assert "No such file or directory" in resp.json["output"]


def test_terminal_api_as_not_admin(api_user):
    """
    Verify only admins are able to use the terminal api endpoint.
    """
    user = api_user()
    assert not user.is_admin
    resp = user.post(
        url_for("api_v1_bp.terminalapi"),
        json={"command": "whoami"},
    )
    assert resp.json == {"output": messages.RESTRICTED_TO_ADMIN}


def test_user_endpoint(api_user):
    """
    Verify GET to /api/v1/user with user authentication.
    """
    user = api_user()
    resp = user.get(
        url_for("api_v1_bp.userapi"),
    )
    assert resp.json == {"logged_in_as": user.email}
