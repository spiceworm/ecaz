from wtforms import validators
from wtforms.fields import EmailField

from application.ui.forms import BaseForm


__all__ = ("ForgotPasswordForm",)


class ForgotPasswordForm(BaseForm):
    email = EmailField(
        "email",
        render_kw={"placeholder": "Email"},
        validators=[
            validators.DataRequired(),
            validators.Email(),
        ],
    )
