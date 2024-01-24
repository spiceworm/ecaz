import flask
import flask_login
import flask_mailman
import psycopg2
import psycopg2.errors
from psycopg2.errorcodes import UNIQUE_VIOLATION
import sqlalchemy.exc

from application.constants import messages
from application.models import (
    ApiToken,
    db,
)
from application.ui import forms


__all__ = (
    "change_password",
    "change_username",
    "send_verify_email",
    "verify_email",
)


@flask_login.login_required
def change_password():
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
    return flask.redirect(flask.url_for(".settings"))


@flask_login.login_required
def change_username():
    form = forms.ChangeUsernameForm()
    if form.validate_on_submit():
        user = flask_login.current_user
        try:
            user.username = form.username.data
            db.session.add(user)
            db.session.commit()
        except sqlalchemy.exc.IntegrityError as e:
            if isinstance(e.orig, psycopg2.errors.lookup(UNIQUE_VIOLATION)):
                db.session.rollback()
                flask.flash(messages.DUPLICATE_USERNAME_ERROR, category="error")
            else:
                raise e
        else:
            flask.flash(messages.USERNAME_UPDATE_SUCCESS, category="success")
    return flask.redirect(flask.url_for(".settings"))


@flask_login.login_required
def send_verify_email():
    user = flask_login.current_user
    if user.is_verified:
        flask.flash(messages.ACCOUNT_ALREADY_VERIFIED, category="info")
    else:
        # Delete any old tokens when a user asks to be sent a verification email
        ApiToken.query.filter(
            ApiToken.name == ApiToken.VERIFY_EMAIL_TAG,
            ApiToken.user == user,
        ).delete()

        token = ApiToken.create_email_verification_token(user)
        url = flask.url_for(".verify_email", jwt=token.value, _external=True)
        email = flask_mailman.EmailMessage(subject="Verify your account", body=url, to=[user.email])
        email.content_subtype = "html"
        email.send()

        flask.flash(messages.VERIFICATION_EMAIL_SENT, category="info")
    return flask.redirect(flask.url_for(".settings"))


@flask_login.login_required
def verify_email(jwt):
    token = ApiToken.query.filter(ApiToken.value == jwt).one_or_none()
    if token and not token.is_expired and ApiToken.VERIFY_EMAIL_TAG in token.tags:
        token.user.is_verified = True
        flask.flash(messages.ACCOUNT_VERIFIED_SUCCESS, category="success")
        db.session.delete(token)
        db.session.commit()
    else:
        flask.flash(messages.INVALID_TOKEN, category="error")
    return flask.redirect(flask.url_for(".settings"))
