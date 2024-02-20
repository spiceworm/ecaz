from wtforms.validators import ValidationError

from application.constants import messages
from application.models import (
    ReservedUsername,
    User,
)


__all__ = (
    "disallow_reserved_usernames",
    "disallow_whitespace",
    "require_unique_username",
    "require_valid_user",
)


def disallow_reserved_usernames(form, field):
    if ReservedUsername.query.filter_by(username=field.data).one_or_none():
        raise ValidationError(messages.RESERVED_USERNAME_ERROR)


def disallow_whitespace(form, field):
    s = field.data.strip()
    if " " in s:
        raise ValidationError(messages.WHITESPACE_NOT_ALLOWED)


def require_unique_username(form, field):
    if User.query.filter_by(username=field.data).one_or_none():
        raise ValidationError(messages.DUPLICATE_USERNAME_ERROR)


def require_valid_user(form, field):
    if not User.query.filter_by(username=field.data).one_or_none():
        raise ValidationError(messages.NO_USER_FOR_PROVIDED_USERNAME)
