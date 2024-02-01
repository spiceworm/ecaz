from flask import url_for

from application.constants import messages


def test_status_endpoint(client):
    """
    Verify GET to /api/v1/status.
    """
    resp = client.get(url_for("api_misc_bp.statusapi"))
    assert resp.json == {"message": "ok"}


def test_terminal_api_as_admin(api_user):
    """
    Verify admins are able to successfully use the terminal api endpoint.
    """
    user = api_user(is_admin=True)
    assert user.is_admin
    resp = user.post(
        url_for("api_misc_bp.terminalapi"),
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
        url_for("api_misc_bp.terminalapi"),
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
        url_for("api_misc_bp.terminalapi"),
        json={"command": "whoami"},
    )
    assert resp.json == {"output": messages.RESTRICTED_TO_ADMIN}
