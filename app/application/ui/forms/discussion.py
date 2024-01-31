from wtforms import (
    HiddenField,
    SelectField,
    StringField,
    validators,
)
from wtforms.widgets import TextArea

from application.ui.forms import BaseForm
from application.ui.forms.validators import disallow_whitespace


__all__ = (
    "CreateCommentForm",
    "CreateThreadForm",
    "CreateTopicForm",
)


class CreateCommentForm(BaseForm):
    body = StringField(
        render_kw={"placeholder": "Enter comment ..."},
        validators=[validators.DataRequired()],
        widget=TextArea(),
    )
    parent_id = HiddenField()


class CreateThreadForm(BaseForm):
    body = StringField(
        validators=[validators.DataRequired()],
        widget=TextArea(),
    )
    title = StringField(
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
        validators=[
            validators.DataRequired(),
            disallow_whitespace,
        ],
    )
