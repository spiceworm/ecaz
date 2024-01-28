from wtforms.validators import ValidationError

from application.constants import messages
from application.models import User


def unique_email(form, field):
    if User.query.filter_by(email=field.data).one_or_none():
        raise ValidationError(messages.DUPLICATE_EMAIL_ERROR)


def unique_username(form, field):
    if User.query.filter_by(username=field.data).one_or_none():
        raise ValidationError(messages.DUPLICATE_USERNAME_ERROR)
