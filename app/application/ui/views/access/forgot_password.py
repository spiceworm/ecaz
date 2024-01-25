import flask
import flask_mailman

from application.constants import messages
from application.models import (
    AuthToken,
    User,
)
from application.ui import forms
from application.util.decorators import require_unauthenticated


__all__ = ("forgot_password",)


@require_unauthenticated(if_authenticated_redirect_to=".profile")
def forgot_password() -> str:
    form = forms.ForgotPasswordForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).one_or_none()
        if user:
            token = AuthToken.create_reset_password_token(user)
            url = flask.url_for(".reset_password", jwt=token.value, _external=True)
            msg = flask_mailman.EmailMessage(subject="Reset Password", body=url, to=[user.email])
            msg.content_subtype = "html"
            msg.send()

        msg = messages.PASSWORD_RESET_EMAIL_SENT
        flask.flash(msg, category="info")
    return flask.render_template("access/forgot_password.html", form=form)
