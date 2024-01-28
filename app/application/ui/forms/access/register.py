import flask_wtf
from wtforms import (
    PasswordField,
    StringField,
    validators,
)
from wtforms.fields import EmailField

from application.ui.forms.validators import (
    unique_email,
    unique_username,
)
from application.util import generate_random_username


__all__ = ("RegisterForm",)


class RegisterForm(flask_wtf.FlaskForm):
    email = EmailField(
        "email",
        render_kw={"placeholder": "Email"},
        validators=[
            validators.DataRequired(),
            validators.Email(),
            unique_email,
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
            unique_username,
        ],
    )
