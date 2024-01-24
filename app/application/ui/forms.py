from flask_wtf import FlaskForm
from wtforms import (
    IntegerField,
    PasswordField,
    StringField,
)
from wtforms.validators import DataRequired


class ChangePassword(FlaskForm):
    password1 = PasswordField(
        "password1",
        render_kw={"placeholder": "New Password"},
        validators=[DataRequired()],
    )
    password2 = PasswordField(
        "password2",
        render_kw={"placeholder": "Repeat Password"},
        validators=[DataRequired()],
    )


class CreateApiToken(FlaskForm):
    token_name = StringField(
        "name",
        render_kw={"placeholder": "Name"},
        validators=[DataRequired()],
    )


class DeleteApiToken(FlaskForm):
    id = IntegerField(
        "id",
        validators=[DataRequired()],
    )


class Login(FlaskForm):
    password = PasswordField(
        "password",
        render_kw={"placeholder": "Password"},
        validators=[DataRequired()],
    )
    username = StringField(
        "username",
        render_kw={"placeholder": "Username"},
        validators=[DataRequired()],
    )


class Logout(FlaskForm):
    pass


class Register(FlaskForm):
    password = PasswordField(
        "password",
        render_kw={"placeholder": "Password"},
        validators=[DataRequired()],
    )
    username = StringField(
        "username",
        render_kw={"placeholder": "Username"},
        validators=[DataRequired()],
    )
