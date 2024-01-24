import re

import click
from flask import Blueprint

from ..models import (
    db,
    User,
)


cli_bp = Blueprint(
    "cli",
    __name__,
)


EMAIL_REGEX = re.compile(r"[^@]+@[^@]+\.[^@]+")


def validate_email(ctx, param, value):
    if not EMAIL_REGEX.match(value):
        raise ValueError("Invalid email address")
    return value


@cli_bp.cli.command('create-admin')
@click.option(
    '--email',
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


@cli_bp.cli.command('mark-admin')
@click.option(
    '--email',
    callback=validate_email,
    prompt="Email",
    type=click.UNPROCESSED,
)
def mark_admin(email):
    """
    Update an existing `User` such that `User.admin == True`
    """
    user = User.query.filter(User.email == email).one_or_none()
    if not user:
        raise ValueError(f"No user with email '{email}' exists")
    user.is_admin = True
    db.session.add(user)
    db.session.commit()
