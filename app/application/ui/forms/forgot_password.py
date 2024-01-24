from flask_wtf import FlaskForm
from wtforms.fields import EmailField
from wtforms import validators


__all__ = ("ForgotPasswordForm",)


class ForgotPasswordForm(FlaskForm):
    email = EmailField(
        "email",
        render_kw={"placeholder": "Email"},
        validators=[
            validators.DataRequired(),
            validators.Email(),
        ],
    )
