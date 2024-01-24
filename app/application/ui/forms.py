from flask_wtf import FlaskForm
from wtforms import (
    PasswordField,
    StringField,
)
from wtforms.validators import DataRequired


class Login(FlaskForm):
    password = PasswordField(
        'password',
        render_kw={"placeholder": "Password"},
        validators=[DataRequired()],
    )
    username = StringField(
        'username',
        render_kw={"placeholder": "Username"},
        validators=[DataRequired()],
    )
