from flask_wtf import FlaskForm
from wtforms import PasswordField
from wtforms import validators
from wtforms.fields import EmailField


__all__ = (
    "ChangePasswordForm",
    "DeleteAccountForm",
    "EmailForm",
)


class ChangePasswordForm(FlaskForm):
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


class DeleteAccountForm(FlaskForm):
    pass


class EmailForm(FlaskForm):
    email = EmailField(
        "email",
        render_kw={"readonly": True},
    )
