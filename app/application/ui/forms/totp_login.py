import flask_wtf
from wtforms import (
    StringField,
    validators,
)


__all__ = (
    "TotpLoginForm",
)


class TotpLoginForm(flask_wtf.FlaskForm):
    totp_code = StringField(
        "totp_code",
        validators=[validators.DataRequired()]
    )
