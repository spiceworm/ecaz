from wtforms import (
    EmailField,
    PasswordField,
    StringField,
    validators,
)

from application.ui.forms import (
    BaseForm,
    filters,
)
from application.ui.forms.validators import (
    disallow_reserved_usernames,
    require_unique_username,
)


__all__ = (
    "ChangeEmailForm",
    "ChangePasswordForm",
    "ChangeUsernameForm",
    "DeleteAccountForm",
    "TotpDisableForm",
    "WebAuthnDisableForm",
)


class ChangeEmailForm(BaseForm):
    email = EmailField(
        "email",
        filters=[filters.strip_whitespace],
        render_kw={"placeholder": "Email"},
        validators=[
            validators.DataRequired(),
            # Email does not have to be unique. Multiple accounts could have the same
            # email, but only the account with the verified email will receive emails.
        ],
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
        filters=[filters.strip_whitespace],
        render_kw={"placeholder": "Username"},
        validators=[
            validators.DataRequired(),
            disallow_reserved_usernames,
            require_unique_username,
        ],
    )


class DeleteAccountForm(BaseForm):
    pass


class TotpDisableForm(BaseForm):
    pass


class WebAuthnDisableForm(BaseForm):
    pass
