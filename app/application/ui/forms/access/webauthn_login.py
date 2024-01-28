from wtforms import (
    HiddenField,
    validators,
)

from application.ui.forms import BaseForm


__all__ = ("WebauthnLoginForm",)


class WebauthnLoginForm(BaseForm):
    credential_authentication_options = HiddenField(
        "credential_authentication_options", validators=[validators.DataRequired()]
    )
