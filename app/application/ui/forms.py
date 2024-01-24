from flask_wtf import FlaskForm
from wtforms import (
    IntegerField,
    PasswordField,
    StringField,
)
from wtforms.fields import EmailField
from wtforms import validators


class ChangePassword(FlaskForm):
    password1 = PasswordField(
        "password1",
        render_kw={"placeholder": "New Password"},
        validators=[
            validators.DataRequired(),
            validators.Length(min=8),
        ],
    )
    password2 = PasswordField(
        "password2",
        render_kw={"placeholder": "Repeat Password"},
        validators=[
            validators.DataRequired(),
            validators.Length(min=8),
        ],
    )


class CreateApiToken(FlaskForm):
    token_name = StringField(
        "name",
        render_kw={"placeholder": "Name"},
        validators=[validators.DataRequired()],
    )


class DeleteApiToken(FlaskForm):
    id = IntegerField(
        "id",
        validators=[validators.DataRequired()],
    )


class Login(FlaskForm):
    email = EmailField(
        "email",
        render_kw={"placeholder": "Email"},
        validators=[
            validators.DataRequired(),
            validators.Email(),
        ],
    )
    password = PasswordField(
        "password",
        render_kw={"placeholder": "Password"},
        validators=[validators.DataRequired()],
    )


class Logout(FlaskForm):
    pass


class Register(FlaskForm):
    email = EmailField(
        "email",
        render_kw={"placeholder": "Email"},
        validators=[
            validators.DataRequired(),
            validators.Email(),
        ],
    )
    password = PasswordField(
        "password",
        render_kw={"placeholder": "Password"},
        validators=[
            validators.DataRequired(),
            validators.Length(min=8),
        ],
    )
