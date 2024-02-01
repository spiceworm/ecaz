from wtforms import (
    PasswordField,
    StringField,
    validators,
)
from wtforms.fields import EmailField

from application.ui.forms import BaseForm
from application.ui.forms.validators import (
    require_unique_email,
    require_unique_username,
)
from application.util.misc import generate_random_username


__all__ = ("RegisterForm",)


class RegisterForm(BaseForm):
    email = EmailField(
        "email",
        render_kw={"placeholder": "Email"},
        validators=[
            validators.DataRequired(),
            validators.Email(),
            require_unique_email,
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
        default=generate_random_username,
        render_kw={"placeholder": "Username"},
        validators=[
            validators.DataRequired(),
            require_unique_username,
        ],
    )
