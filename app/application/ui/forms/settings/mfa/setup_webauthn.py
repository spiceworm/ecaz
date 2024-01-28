from wtforms import (
    HiddenField,
    validators,
)

from application.ui.forms import BaseForm


__all__ = ("SetupWebauthnForm",)


class SetupWebauthnForm(BaseForm):
    credential_creation_options = HiddenField(
        "credential_creation_options", validators=[validators.DataRequired()]
    )
