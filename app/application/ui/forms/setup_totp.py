import flask_wtf
from wtforms import (
    StringField,
    validators,
)


__all__ = (
    "SetupTotpForm",
)


class SetupTotpForm(flask_wtf.FlaskForm):
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
