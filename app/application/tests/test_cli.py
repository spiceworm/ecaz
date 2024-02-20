import flask

from application.constants import messages
from application.models import ReservedUsername


def test_add_reserved_username_with_from_file(cli_runner):
    """
    Verify reserved usernames can be added using `flask cli add-reserved-entries --file-path=<file-path>`
    """
    fp = "/tmp/reserved-usernames/reserved-usernames.txt"
    with open(fp) as f:
        entries_count = len(f.readlines())
    cli_runner.invoke(args=["cli", "add-reserved-username", f"--from-file={fp}"])
    assert ReservedUsername.query.count() == entries_count


def test_add_reserved_username_with_usernames(cli_runner):
    """
    Verify reserved usernames can be added using `flask cli add-reserved-entries --usernames=<usernames>`
    """
    usernames = {"admin", "administrator", "mod"}
    cli_runner.invoke(args=["cli", "add-reserved-username", f"--usernames={','.join(usernames)}"])
    for obj in ReservedUsername.query.all():
        assert obj.username in usernames
        usernames.remove(obj.username)
    assert len(usernames) == 0


def test_get_config(cli_runner):
    """
    Verify `flask cli get-config returns at least 1 configured variable.
    """
    result = cli_runner.invoke(args=["cli", "get-config"])
    assert f"APP_NAME={flask.current_app.config['APP_NAME']}" in result.output


def test_get_endpoints(cli_runner):
    """
    Verify `flask cli get-endpoints returns at least 1 endpoint to URL path mapping.
    """
    result = cli_runner.invoke(args=["cli", "get-endpoints"])
    assert "ui_bp.login -> /" in result.output


def test_mark_admin(cli_runner, user):
    """
    Verify `flask cli mark-admin --email <email>` sets `User.is_admin = True` for an existing
    `User` entry.
    """
    u = user()
    assert not u.is_admin
    cli_runner.invoke(
        args=[
            "cli",
            "mark-admin",
            "--username",
            u.username,
        ]
    )
    assert u.is_admin


def test_mark_admin_for_non_user(cli_runner):
    """
    Verify `flask cli mark-admin --email <non-existent-email>` produces an error.
    """
    result = cli_runner.invoke(
        args=[
            "cli",
            "mark-admin",
            "--username",
            "not-a-user",
        ]
    )
    assert messages.NO_USER_FOR_PROVIDED_USERNAME in result.output


def test_send_email(cli_runner):
    """
    Verify `flask cli send-email` works as expected.
    """
    result = cli_runner.invoke(
        args=["cli", "send-email", "--subject=Test", "--to=user@test.com", "--body=Body", "--is-html"]
    )
    assert "Sent status: True" in result.output


def test_send_email_failure(cli_runner, mock_email_send):
    """
    Verify `flask cli send-email` works as expected when it fails.
    """
    mock_email_send(lambda self: False)
    result = cli_runner.invoke(
        args=["cli", "send-email", "--subject=Test", "--to=user@test.com", "--body=Body", "--is-html"]
    )
    assert "Sent status: False" in result.output
