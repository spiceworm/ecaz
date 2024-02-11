from wtforms.validators import ValidationError

from application.constants import messages
from application.models import User


__all__ = (
    "disallow_whitespace",
    "require_unique_username",
)


def disallow_whitespace(form, field):
    s = field.data.strip()
    if " " in s:
        raise ValidationError(messages.WHITESPACE_NOT_ALLOWED)


def require_unique_username(form, field):
    if User.query.filter_by(username=field.data).one_or_none():
        raise ValidationError(messages.DUPLICATE_USERNAME_ERROR)
