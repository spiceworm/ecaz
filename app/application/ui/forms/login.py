from flask_wtf import FlaskForm
from wtforms import PasswordField
from wtforms.fields import EmailField
from wtforms import validators


__all__ = ("LoginForm",)


class LoginForm(FlaskForm):
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
        validators=[validators.DataRequired()],
    )
