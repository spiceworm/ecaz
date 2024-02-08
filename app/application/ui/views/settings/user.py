import flask
import flask_login
from werkzeug.wrappers import Response

from application.constants import messages
from application.models import (
    AuthToken,
    db,
)
from application.ui import forms
from application.util.decorators import validate_jwt_as_auth_token


__all__ = (
    "change_email",
    "change_password",
    "change_username",
    "verify_email",
)


@flask_login.login_required
def change_email() -> Response:
    form = forms.ChangeEmailForm()
    if form.validate_on_submit():
        user = flask_login.current_user
        user.is_verified = False
        user.email = form.email.data
        db.session.add(user)
        db.session.commit()
        flask.flash(messages.EMAIL_UPDATE_SUCCESS, category="success")

    return flask.redirect(flask.url_for("ui_bp.settings"))


@flask_login.login_required
def change_password() -> Response:
    form = forms.ChangePasswordForm()
    if form.validate_on_submit():
        password1 = form.password1.data
        password2 = form.password2.data
        if password1 == password2:
            user = flask_login.current_user
            user.password = password1
            db.session.add(user)
            db.session.commit()
            flask.flash(messages.PASSWORD_UPDATE_SUCCESS, category="success")
        else:
            flask.flash(messages.PASSWORD_UPDATE_MATCH_ERROR, category="error")
    return flask.redirect(flask.url_for("ui_bp.settings"))


@flask_login.login_required
def change_username() -> Response:
    form = forms.ChangeUsernameForm()
    if form.validate_on_submit():
        user = flask_login.current_user
        user.username = form.username.data
        db.session.add(user)
        db.session.commit()
        flask.flash(messages.USERNAME_UPDATE_SUCCESS, category="success")
    return flask.redirect(flask.url_for("ui_bp.settings"))


@flask_login.login_required
@validate_jwt_as_auth_token(require_tags=[AuthToken.VERIFY_EMAIL_TAG], error_redirect="ui_bp.settings")
def verify_email(token) -> Response:
    token.user.is_verified = True
    flask.flash(messages.ACCOUNT_VERIFIED_SUCCESS, category="success")
    db.session.delete(token)
    db.session.commit()
    return flask.redirect(flask.url_for("ui_bp.settings"))
