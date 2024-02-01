import re

import click
import flask
import flask_mailman

from application.constants import messages
from application.models import (
    db,
    User,
)
from application.util.misc import csv_to_list


cli_bp = flask.Blueprint(
    "cli",
    __name__,
)


EMAIL_REGEX = re.compile(r"[^@]+@[^@]+\.[^@]+")


def validate_email(ctx, param, value):
    if not EMAIL_REGEX.match(value):
        raise click.BadParameter(messages.INVALID_EMAIL_ADDRESS)
    return value


@cli_bp.cli.command("create-admin")
@click.option(
    "--email",
    callback=validate_email,
    prompt="Email",
    type=click.UNPROCESSED,
)
@click.option(
    "--password",
    confirmation_prompt=True,
    hide_input=True,
    prompt=True,
)
def create_admin(email, password):
    """
    Create a new admin `User` with the provided email and password.
    """
    user = User(
        email=email,
        password=password,
        is_admin=True,
    )
    db.session.add(user)
    db.session.commit()


@cli_bp.cli.command("get-config")
def get_config():
    """
    Show config for current running app.
    """
    for k, v in sorted(flask.current_app.config.items()):
        click.echo(f"{k}={v}")


@cli_bp.cli.command("get-endpoints")
def get_endpoints():
    """
    Show all URL endpoints and the URL path they map to.
    """
    for obj in flask.current_app.url_map.iter_rules():
        click.echo(f"{obj.endpoint} -> {obj.rule}")


@cli_bp.cli.command("mark-admin")
@click.option(
    "--email",
    callback=validate_email,
    prompt="Email",
    type=click.UNPROCESSED,
)
def mark_admin(email):
    """
    Update an existing `User` such that `User.admin == True`
    """
    if user := User.query.filter(User.email == email).one_or_none():
        user.is_admin = True
        db.session.add(user)
        db.session.commit()
    else:
        raise click.UsageError(messages.NO_USER_FOR_PROVIDED_EMAIL)


@click.option(
    "--subject",
    prompt="Subject",
    type=click.UNPROCESSED,
)
@click.option(
    "--to",
    prompt="Recipient",
    type=click.UNPROCESSED,
)
@click.option(
    "--body",
    prompt="Body",
    type=click.UNPROCESSED,
)
@click.option(
    "--is-html",
    is_flag=True,
)
@cli_bp.cli.command("send-email")
def send_email(subject, to, body, is_html):
    """
    Send an email.
    """
    msg = flask_mailman.EmailMessage(subject=subject, body=body, to=csv_to_list(to))
    if is_html:
        msg.content_subtype = "html"
    status = bool(msg.send())
    click.echo(f"Sent status: {status}")
