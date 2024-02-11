from wtforms import (
    PasswordField,
    StringField,
    validators,
)

from application.ui.forms import BaseForm


__all__ = ("LoginForm",)


class LoginForm(BaseForm):
    password = PasswordField(
        "password",
        render_kw={"placeholder": "Password"},
        validators=[validators.DataRequired()],
    )
    username = StringField(
        "username",
        render_kw={"placeholder": "Username"},
        validators=[
            validators.DataRequired(),
        ],
    )
