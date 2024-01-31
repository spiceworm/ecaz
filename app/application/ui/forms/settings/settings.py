from wtforms import (
    EmailField,
    PasswordField,
    StringField,
    validators,
)

from application.ui.forms import BaseForm
from application.ui.forms.validators import require_unique_username


__all__ = (
    "ChangePasswordForm",
    "ChangeUsernameForm",
    "DeleteAccountForm",
    "EmailForm",
    "TotpDisableForm",
    "WebAuthnDisableForm",
)


class ChangePasswordForm(BaseForm):
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


class ChangeUsernameForm(BaseForm):
    username = StringField(
        "username",
        render_kw={"placeholder": "Username"},
        validators=[
            validators.DataRequired(),
            require_unique_username,
        ],
    )


class DeleteAccountForm(BaseForm):
    pass


class EmailForm(BaseForm):
    email = EmailField(
        "email",
        render_kw={"readonly": True},
    )


class TotpDisableForm(BaseForm):
    pass


class WebAuthnDisableForm(BaseForm):
    pass
