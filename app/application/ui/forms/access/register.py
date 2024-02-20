from wtforms import (
    PasswordField,
    StringField,
    validators,
)
from wtforms.fields import EmailField

from application.ui.forms import BaseForm
from application.ui.forms.validators import (
    disallow_reserved_usernames,
    require_unique_username,
)
from application.util.misc import generate_unique_username


__all__ = ("RegisterForm",)


class RegisterForm(BaseForm):
    email = EmailField(
        "email",
        render_kw={"placeholder": "Email"},
        validators=[
            validators.DataRequired(),
            validators.Email(),
            # Email does not have to be unique. Multiple accounts could have the same
            # email, but only the account with the verified email will receive emails.
        ],
    )
    password = PasswordField(
        "password",
        render_kw={"placeholder": "Password"},
        validators=[
            validators.DataRequired(),
            validators.Length(min=8),
        ],
    )
    username = StringField(
        "username",
        default=generate_unique_username,
        render_kw={"placeholder": "Username"},
        validators=[
            validators.DataRequired(),
            disallow_reserved_usernames,
            require_unique_username,
        ],
    )
