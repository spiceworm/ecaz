from wtforms import (
    StringField,
    validators,
)

from application.ui.forms import BaseForm


__all__ = ("TotpLoginForm",)


class TotpLoginForm(BaseForm):
    totp_code = StringField("totp_code", validators=[validators.DataRequired()])
