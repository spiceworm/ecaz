from wtforms import (
    BooleanField,
    HiddenField,
    SelectField,
    StringField,
    validators,
)
from wtforms.widgets import TextArea

from application.constants import sort_by
from application.ui.forms import (
    BaseForm,
    filters,
)
from application.ui.forms.mixins import ExpiresAtMixin
from application.ui.forms.validators import (
    disallow_whitespace,
    require_valid_user,
)


__all__ = (
    "CreateCommentForm",
    "CreateThreadForm",
    "CreateTopicForm",
    "CreateTopicBanForm",
    "SortCommentsForm",
    "SortThreadsForm",
    "SortTopicsForm",
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


class CreateTopicBanForm(ExpiresAtMixin, BaseForm):
    is_shadow = BooleanField("is_shadow")
    reason = StringField(
        render_kw={"placeholder": "Reason"},
        validators=[
            validators.DataRequired(),
        ],
    )
    username = StringField(
        filters=[filters.strip_whitespace],
        render_kw={"placeholder": "Username"},
        validators=[
            validators.DataRequired(),
            require_valid_user,
        ],
    )


class SortCommentsForm(BaseForm):
    sorting = SelectField(
        choices=[
            (sort_by.TOP, sort_by.TOP),
            (sort_by.NEW, sort_by.NEW),
        ],
        default=sort_by.COMMENTS_DEFAULT,
    )


class SortThreadsForm(BaseForm):
    sorting = SelectField(
        choices=[
            (sort_by.TOP, sort_by.TOP),
            (sort_by.NEW, sort_by.NEW),
        ],
        default=sort_by.THREADS_DEFAULT,
    )


class SortTopicsForm(BaseForm):
    sorting = SelectField(
        choices=[
            (sort_by.TOP, sort_by.TOP),
            (sort_by.NEW, sort_by.NEW),
            (sort_by.ALPHABETICAL, sort_by.ALPHABETICAL),
            (sort_by.REVERSE_ALPHABETICAL, sort_by.REVERSE_ALPHABETICAL),
        ],
        default=sort_by.TOPICS_DEFAULT,
    )
