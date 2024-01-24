import flask_wtf
from wtforms import (
    HiddenField,
    validators,
)


__all__ = (
    "WebauthnLoginForm",
)


class WebauthnLoginForm(flask_wtf.FlaskForm):
    credential_authentication_options = HiddenField(
        "credential_authentication_options",
        validators=[validators.DataRequired()]
    )
