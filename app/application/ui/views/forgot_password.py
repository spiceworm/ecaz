import flask
import flask_login
from flask_mailman import EmailMessage

from .. import forms
from ...constants import messages
from ...models import (
    ApiToken,
    User,
)


__all__ = ("forgot_password",)


def forgot_password():
    if flask_login.current_user.is_authenticated:
        return flask.redirect(flask.url_for(".profile"))

    form = forms.ForgotPasswordForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).one_or_none()
        if user:
            # Delete any old tokens from prior password reset requests
            ApiToken.query.filter(
                ApiToken.name == ApiToken.RESET_PASSWORD_TAG,
                ApiToken.user == user,
            ).delete()

            token = ApiToken.create_reset_password_token(user)
            url = flask.url_for(".reset_password", jwt=token.value, _external=True)
            msg = EmailMessage(subject="Reset Password", body=url, to=[user.email])
            msg.content_subtype = "html"
            msg.send()

        msg = messages.PASSWORD_RESET_EMAIL_SENT
        flask.flash(msg, category="info")
    return flask.render_template("forgot_password.html", form=form)
