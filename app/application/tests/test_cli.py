from application.constants import messages
from application.models import User


def test_create_admin(cli_runner):
    email = "user@test.com"
    assert User.query.filter_by(email=email).one_or_none() is None
    cli_runner.invoke(
        args=[
            "cli", "create-admin", "--email", email, "--password", "the-password"
        ]
    )
    user = User.query.filter_by(email=email).one_or_none()
    assert user.is_admin


def test_create_admin_using_invalid_email(cli_runner):
    result = cli_runner.invoke(
        args=[
            "cli", "create-admin", "--email", "not-an-email", "--password", "the-password"
        ]
    )
    assert messages.INVALID_EMAIL_ADDRESS in result.output


def test_mark_admin(cli_runner, user):
    u = user()
    assert not u.is_admin
    cli_runner.invoke(
        args=[
            "cli", "mark-admin", "--email", u.email,
        ]
    )
    assert u.is_admin


def test_mark_admin_for_non_user(cli_runner):
    result = cli_runner.invoke(
        args=[
            "cli", "mark-admin", "--email", "not-a-user@test.com",
        ]
    )
    assert messages.NO_USER_FOR_PROVIDED_EMAIL in result.output


def test_mark_admin_using_invalid_email(cli_runner):
    result = cli_runner.invoke(
        args=[
            "cli", "mark-admin", "--email", "not-an-email"
        ]
    )
    assert messages.INVALID_EMAIL_ADDRESS in result.output
