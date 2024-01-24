import flask_wtf
from wtforms import (
    EmailField,
    PasswordField,
    StringField,
    validators,
)


__all__ = (
    "ChangePasswordForm",
    "ChangeUsernameForm",
    "DeleteAccountForm",
    "EmailForm",
)


class ChangePasswordForm(flask_wtf.FlaskForm):
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


class ChangeUsernameForm(flask_wtf.FlaskForm):
    username = StringField(
        "username",
        render_kw={"placeholder": "Username"},
        validators=[
            validators.DataRequired(),
        ],
    )


class DeleteAccountForm(flask_wtf.FlaskForm):
    pass


class EmailForm(flask_wtf.FlaskForm):
    email = EmailField(
        "email",
        render_kw={"readonly": True},
    )
