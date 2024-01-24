from datetime import timedelta

import flask
from flask_jwt_extended import create_access_token
import flask_login
from flask_mailman import EmailMessage

from .. import forms
from ...constants import messages
from ...models import (
    ApiToken,
    db,
    User,
)


__all__ = ("forgot_password",)


def forgot_password():
    if flask_login.current_user.is_authenticated:
        return flask.redirect(flask.url_for(".profile"))

    form = forms.ForgotPasswordForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).one_or_none()
        if user is not None:
            token_name = "forgot-password"

            # Delete any old tokens from prior password reset requests
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

            url = flask.url_for(".reset_password", jwt=token_value, _external=True)
            msg = EmailMessage(subject="Reset Password", body=url, to=[user.email])
            msg.content_subtype = "html"
            msg.send()

        msg = messages.PASSWORD_RESET_EMAIL_SENT.format(email=user.email)
        flask.flash(msg, category="info")
    return flask.render_template("forgot_password.html", form=form)
