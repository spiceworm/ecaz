from wtforms import (
    IntegerField,
    StringField,
    validators,
)

from application.ui.forms import (
    BaseForm,
    filters,
)
from application.ui.forms.mixins import ExpiresAtMixin


__all__ = (
    "CreateAuthTokenForm",
    "DeleteAuthTokenForm",
)


class CreateAuthTokenForm(ExpiresAtMixin, BaseForm):
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
