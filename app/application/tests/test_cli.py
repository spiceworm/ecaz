from application.constants import messages
from application.models import User


def test_create_admin(cli_runner):
    """
    Verify `flask cli create-admin --email <email> --password <password>` creates a new `User`
    where `User.is_admin == True`.
    """
    email = "user@test.com"
    assert User.query.filter_by(email=email).one_or_none() is None
    cli_runner.invoke(args=["cli", "create-admin", "--email", email, "--password", "the-password"])
    user = User.query.filter_by(email=email).one_or_none()
    assert user.is_admin


def test_create_admin_using_invalid_email(cli_runner):
    """
    Verify `flask cli create-admin --email <bad-email> --password <password>` produces an error.
    """
    result = cli_runner.invoke(
        args=["cli", "create-admin", "--email", "not-an-email", "--password", "the-password"]
    )
    assert messages.INVALID_EMAIL_ADDRESS in result.output


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
            "--email",
            u.email,
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
            "--email",
            "not-a-user@test.com",
        ]
    )
    assert messages.NO_USER_FOR_PROVIDED_EMAIL in result.output


def test_mark_admin_using_invalid_email(cli_runner):
    """
    Verify `flask cli mark-admin --email <invalid-email>` produces an error.
    """
    result = cli_runner.invoke(args=["cli", "mark-admin", "--email", "not-an-email"])
    assert messages.INVALID_EMAIL_ADDRESS in result.output
