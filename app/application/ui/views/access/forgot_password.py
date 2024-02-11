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


@require_unauthenticated(if_authenticated_redirect_to="ui_bp.profile")
def forgot_password() -> str:
    form = forms.ForgotPasswordForm()
    if form.validate_on_submit():
        if user := User.query.filter_by(email=form.email.data, is_verified=True).one_or_none():
            token = AuthToken.create_reset_password_token(user)
            url = flask.url_for(".reset_password", jwt=token.value, _external=True)
            msg = flask_mailman.EmailMessage(subject="Reset Password", body=url, to=[user.email])
            msg.content_subtype = "html"
            msg.send()
            flask.flash(messages.PASSWORD_RESET_EMAIL_SENT, category="info")
        else:
            flask.flash(messages.USER_NOT_FOUND_OR_EMAIL_NOT_VERIFIED, category="error")
    return flask.render_template("access/forgot_password.html", form=form)
