import flask

from application.constants import messages
from application.models import (
    AuthToken,
    db,
)
from application.ui import forms
from application.util import process_jwt_auth_token


__all__ = ("reset_password",)


@process_jwt_auth_token(
    require_tags=[AuthToken.RESET_PASSWORD_TAG], error_redirect=".forgot_password"
)
def reset_password(token):
    form = forms.ResetPasswordForm()
    if form.validate_on_submit():
        password1 = form.password1.data
        password2 = form.password2.data
        if password1 == password2:
            token.user.password = password1
            db.session.add(token.user)
            db.session.delete(token)
            db.session.commit()
            flask.flash(messages.PASSWORD_UPDATE_SUCCESS, category="success")
            return flask.redirect(flask.url_for(".login"))
        else:
            flask.flash(messages.PASSWORD_UPDATE_MATCH_ERROR, category="error")
    return flask.render_template("access/reset_password.html", form=form, jwt=token.value)
