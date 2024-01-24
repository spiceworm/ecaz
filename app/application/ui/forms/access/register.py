import flask_wtf
from wtforms import (
    PasswordField,
    validators,
)
from wtforms.fields import EmailField


__all__ = ("RegisterForm",)


class RegisterForm(flask_wtf.FlaskForm):
    email = EmailField(
        "email",
        render_kw={"placeholder": "Email"},
        validators=[
            validators.DataRequired(),
            validators.Email(),
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
