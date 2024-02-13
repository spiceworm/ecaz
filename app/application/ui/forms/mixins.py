from wtforms import (
    IntegerField,
    SelectField,
)

from application.constants import expires


class ExpiresAtMixin:
    expires_at_number = IntegerField(
        "expires_at_number",
        render_kw={"disabled": True},
        default=0,
    )
    expires_at_unit = SelectField(
        "expires_at_unit",
        choices=[
            (expires.NEVER, expires.NEVER),
            (expires.UNIT_MICROSECONDS, expires.UNIT_MICROSECONDS),
            (expires.UNIT_MILLISECONDS, expires.UNIT_MILLISECONDS),
            (expires.UNIT_SECONDS, expires.UNIT_SECONDS),
            (expires.UNIT_MINUTES, expires.UNIT_MINUTES),
            (expires.UNIT_HOURS, expires.UNIT_HOURS),
            (expires.UNIT_DAYS, expires.UNIT_DAYS),
            (expires.UNIT_WEEKS, expires.UNIT_WEEKS),
        ],
        default=expires.NEVER,
    )
