import flask_wtf
from wtforms import (
    BooleanField,
    IntegerField,
    SelectField,
    StringField,
    validators,
)


__all__ = (
    "CreateApiTokenForm",
    "DeleteApiTokenForm",
)


class CreateApiTokenForm(flask_wtf.FlaskForm):
    EXPIRES_NEVER = "Never"
    EXPIRES_UNIT_MICROSECONDS = "Microseconds"
    EXPIRES_UNIT_MILLISECONDS = "Milliseconds"
    EXPIRES_UNIT_SECONDS = "Seconds"
    EXPIRES_UNIT_MINUTES = "Minutes"
    EXPIRES_UNIT_HOURS = "Hours"
    EXPIRES_UNIT_DAYS = "Days"
    EXPIRES_UNIT_WEEKS = "Weeks"

    expires_number = IntegerField(
        "expires_number",
        render_kw={"disabled": True},
        default=0,
    )
    expires_unit = SelectField(
        "expires_unit",
        choices=[
            (EXPIRES_NEVER, EXPIRES_NEVER),
            (EXPIRES_UNIT_MICROSECONDS, EXPIRES_UNIT_MICROSECONDS),
            (EXPIRES_UNIT_MILLISECONDS, EXPIRES_UNIT_MILLISECONDS),
            (EXPIRES_UNIT_SECONDS, EXPIRES_UNIT_SECONDS),
            (EXPIRES_UNIT_MINUTES, EXPIRES_UNIT_MINUTES),
            (EXPIRES_UNIT_HOURS, EXPIRES_UNIT_HOURS),
            (EXPIRES_UNIT_DAYS, EXPIRES_UNIT_DAYS),
            (EXPIRES_UNIT_WEEKS, EXPIRES_UNIT_WEEKS),
        ],
        default=EXPIRES_NEVER,
    )
    token_name = StringField(
        "name",
        render_kw={"placeholder": "Name"},
        validators=[validators.DataRequired()],
    )


class DeleteApiTokenForm(flask_wtf.FlaskForm):
    id = IntegerField(
        "id",
        validators=[validators.DataRequired()],
    )
