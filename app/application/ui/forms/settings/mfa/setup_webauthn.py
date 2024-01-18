import flask_wtf
from wtforms import (
    HiddenField,
    validators,
)


__all__ = (
    "SetupWebauthnForm",
)


class SetupWebauthnForm(flask_wtf.FlaskForm):
    credential_creation_options = HiddenField(
        "credential_creation_options",
        validators=[validators.DataRequired()]
    )
