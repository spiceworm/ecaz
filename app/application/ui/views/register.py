from datetime import timedelta

import flask
from flask_jwt_extended import create_access_token
import flask_login
from flask_mailman import EmailMessage
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
        password_hash = flask.g.bcrypt.generate_password_hash(form.password.data).decode("utf-8")
        user = User(
            email=form.email.data,
            password_hash=password_hash,
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
        token_name = "verify-email"

        # Delete any old tokens when a user asks to be sent a verification email
        ApiToken.query.filter(
            ApiToken.name == token_name,
            ApiToken.user == user,
        ).delete()

        token_value = create_access_token(
            additional_claims={"tags": ["hidden"]},
            expires_delta=timedelta(hours=24),
            identity=user.email,
        )
        api_token = ApiToken(
            name=token_name,
            value=token_value,
            user=user,
        )
        db.session.add(api_token)
        db.session.commit()

        url = flask.url_for(".verify_account", jwt=token_value, _external=True)
        email = EmailMessage(subject="Verify your account", body=url, to=[user.email])
        email.content_subtype = "html"
        email.send()

        msg = messages.VERIFICATION_EMAIL_SENT.format(email=user.email)
        flask.flash(msg, category="info")
    return flask.redirect(flask.request.referrer)


@flask_login.login_required
def verify_account(jwt):
    token = ApiToken.query.filter(ApiToken.value == jwt).one_or_none()
    if token:
        if token.is_expired:
            flask.flash(messages.ACCOUNT_VERIFICATION_TOKEN_EXPIRED, category="error")
        else:
            token.user.verified = True
            flask.flash(messages.ACCOUNT_VERIFIED_SUCCESS, category="success")
        db.session.delete(token)
        db.session.commit()
    else:
        flask.flash(messages.INVALID_ACCOUNT_VERIFICATION_TOKEN, category="error")
    return flask.redirect(flask.url_for(".settings"))
