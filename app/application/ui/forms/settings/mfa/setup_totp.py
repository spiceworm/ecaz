from wtforms import (
    StringField,
    validators,
)

from application.ui.forms import BaseForm


__all__ = ("SetupTotpForm",)


class SetupTotpForm(BaseForm):
    setup_secret = StringField(
        "setup_secret",
        render_kw={"disabled": True},
    )
    totp_code = StringField(
        "totp_code",
        render_kw={"placeholder": "TOTP code"},
        validators=[
            validators.DataRequired(),
        ],
    )
