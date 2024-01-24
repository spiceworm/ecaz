import flask_wtf
from wtforms import (
    IntegerField,
    StringField,
    validators,
)


__all__ = (
    "CreateApiTokenForm",
    "DeleteApiTokenForm",
)


class CreateApiTokenForm(flask_wtf.FlaskForm):
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
