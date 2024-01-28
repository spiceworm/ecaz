from wtforms import (
    PasswordField,
    validators,
)

from application.ui.forms import BaseForm


__all__ = ("ResetPasswordForm",)


class ResetPasswordForm(BaseForm):
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
