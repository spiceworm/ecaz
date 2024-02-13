from wtforms import (
    IntegerField,
    SelectField,
    StringField,
    validators,
)

from application.ui.forms import (
    BaseForm,
    filters,
)


__all__ = (
    "CreateAuthTokenForm",
    "DeleteAuthTokenForm",
)


class CreateAuthTokenForm(BaseForm):
    EXPIRES_NEVER = "Never"
    EXPIRES_UNIT_MICROSECONDS = "Microseconds"
    EXPIRES_UNIT_MILLISECONDS = "Milliseconds"
    EXPIRES_UNIT_SECONDS = "Seconds"
    EXPIRES_UNIT_MINUTES = "Minutes"
    EXPIRES_UNIT_HOURS = "Hours"
    EXPIRES_UNIT_DAYS = "Days"
    EXPIRES_UNIT_WEEKS = "Weeks"

    expires_at_number = IntegerField(
        "expires_at_number",
        render_kw={"disabled": True},
        default=0,
    )
    expires_at_unit = SelectField(
        "expires_at_unit",
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
        filters=[filters.strip_whitespace],
        render_kw={"placeholder": "Name"},
        validators=[validators.DataRequired()],
    )


class DeleteAuthTokenForm(BaseForm):
    id = IntegerField(
        "id",
        validators=[validators.DataRequired()],
    )
