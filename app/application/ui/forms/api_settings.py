from flask_wtf import FlaskForm
from wtforms import (
    IntegerField,
    StringField,
)
from wtforms import validators


__all__ = (
    "CreateApiTokenForm",
    "DeleteApiTokenForm",
)


class CreateApiTokenForm(FlaskForm):
    token_name = StringField(
        "name",
        render_kw={"placeholder": "Name"},
        validators=[validators.DataRequired()],
    )


class DeleteApiTokenForm(FlaskForm):
    id = IntegerField(
        "id",
        validators=[validators.DataRequired()],
    )
