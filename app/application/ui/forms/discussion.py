from wtforms import (
    BooleanField,
    HiddenField,
    IntegerField,
    SelectField,
    StringField,
    validators,
)
from wtforms.widgets import TextArea

from application.ui.forms import (
    BaseForm,
    filters,
)
from application.ui.forms.validators import (
    disallow_whitespace,
    require_valid_user,
)


__all__ = (
    "CreateCommentForm",
    "CreateThreadForm",
    "CreateTopicForm",
    "CreateTopicBanForm",
)


class CreateCommentForm(BaseForm):
    body = StringField(
        filters=[filters.strip_whitespace],
        render_kw={"placeholder": "Enter comment ..."},
        validators=[validators.DataRequired()],
        widget=TextArea(),
    )
    parent_id = HiddenField()


class CreateThreadForm(BaseForm):
    body = StringField(
        filters=[filters.strip_whitespace],
        validators=[validators.DataRequired()],
        widget=TextArea(),
    )
    title = StringField(
        filters=[filters.strip_whitespace],
        validators=[validators.DataRequired()],
    )
    topic_id = SelectField(
        validators=[validators.DataRequired()],
    )


class CreateTopicForm(BaseForm):
    description = StringField(
        validators=[validators.DataRequired()],
        widget=TextArea(),
    )
    name = StringField(
        filters=[filters.strip_whitespace],
        validators=[
            validators.DataRequired(),
            disallow_whitespace,
        ],
    )
    is_private = BooleanField()


class CreateTopicBanForm(BaseForm):
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
    is_shadow = BooleanField("is_shadow")
    reason = StringField(
        "reason",
        render_kw={"placeholder": "Reason"},
        validators=[
            validators.DataRequired(),
        ],
    )
    username = StringField(
        "username",
        filters=[filters.strip_whitespace],
        render_kw={"placeholder": "Username"},
        validators=[
            validators.DataRequired(),
            require_valid_user,
        ],
    )
