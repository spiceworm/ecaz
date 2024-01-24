import flask_wtf
from wtforms import (
    PasswordField,
    validators,
)


__all__ = ("ResetPasswordForm",)


class ResetPasswordForm(flask_wtf.FlaskForm):
    password1 = PasswordField(
        "password1",
        render_kw={"placeholder": "New Password"},
        validators=[
            validators.DataRequired(),
            validators.Length(min=8),
        ],
    )
    password2 = PasswordField(
        "password2",
        render_kw={"placeholder": "Repeat Password"},
        validators=[
            validators.DataRequired(),
            validators.Length(min=8),
        ],
    )
