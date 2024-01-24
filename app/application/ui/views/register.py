import flask
import flask_login
import flask_mailman
import psycopg2.errors
from psycopg2.errorcodes import UNIQUE_VIOLATION
import sqlalchemy.exc

from .. import forms
from ...constants import messages
from ...models import (
    ApiToken,
    db,
    User,
)


__all__ = (
    "register",
    "send_verify_email",
    "verify_account",
)


def register():
    if flask_login.current_user.is_authenticated:
        return flask.redirect(flask.url_for(".profile"))

    form = forms.RegisterForm()
    if form.validate_on_submit():
        user = User(
            email=form.email.data,
            password=form.password.data,
        )
        db.session.add(user)
        try:
            db.session.commit()
        except sqlalchemy.exc.IntegrityError as e:
            if isinstance(e.orig, psycopg2.errors.lookup(UNIQUE_VIOLATION)):
                flask.flash(messages.DUPLICATE_EMAIL_ERROR, category="error")
            else:
                raise e
        else:
            flask_login.login_user(user)
            return flask.redirect(flask.url_for(".profile"))
    return flask.render_template("register.html", form=form)


@flask_login.login_required
def send_verify_email():
    user = flask_login.current_user
    if user.verified:
        flask.flash(messages.ACCOUNT_ALREADY_VERIFIED, category="info")
    else:
        # Delete any old tokens when a user asks to be sent a verification email
        ApiToken.query.filter(
            ApiToken.name == ApiToken.VERIFY_EMAIL_TAG,
            ApiToken.user == user,
        ).delete()

        token = ApiToken.create_email_verification_token(user)
        url = flask.url_for(".verify_account", jwt=token.value, _external=True)
        email = flask_mailman.EmailMessage(subject="Verify your account", body=url, to=[user.email])
        email.content_subtype = "html"
        email.send()

        flask.flash(messages.VERIFICATION_EMAIL_SENT, category="info")
    return flask.redirect(flask.request.referrer)


@flask_login.login_required
def verify_account(jwt):
    token = ApiToken.query.filter(ApiToken.value == jwt).one_or_none()
    if token and ApiToken.VERIFY_EMAIL_TAG in token.tags:
        if token.is_expired:
            flask.flash(messages.TOKEN_EXPIRED, category="error")
        else:
            token.user.verified = True
            flask.flash(messages.ACCOUNT_VERIFIED_SUCCESS, category="success")
        db.session.delete(token)
        db.session.commit()
    else:
        flask.flash(messages.INVALID_TOKEN, category="error")
    return flask.redirect(flask.url_for(".settings"))
