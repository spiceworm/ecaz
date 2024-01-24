import flask_wtf
from wtforms import validators
from wtforms.fields import EmailField


__all__ = ("ForgotPasswordForm",)


class ForgotPasswordForm(flask_wtf.FlaskForm):
    email = EmailField(
        "email",
        render_kw={"placeholder": "Email"},
        validators=[
            validators.DataRequired(),
            validators.Email(),
        ],
    )
