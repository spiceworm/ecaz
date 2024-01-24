import flask

from .. import forms
from ...constants import messages
from ...models import (
    ApiToken,
    db,
)

__all__ = ("reset_password",)


def reset_password(jwt):
    form = forms.ResetPasswordForm()
    token = ApiToken.query.filter(ApiToken.value == jwt).one_or_none()

    if not token or ApiToken.RESET_PASSWORD_TAG not in token.tags or token.is_expired:
        flask.flash(messages.INVALID_TOKEN, category="error")
        return flask.redirect(flask.url_for(".forgot_password"))

    if form.validate_on_submit():
        password1 = form.password1.data
        password2 = form.password2.data
        if password1 != password2:
            flask.flash(messages.PASSWORD_UPDATE_MATCH_ERROR, category="error")
        else:
            user = token.user
            user.password = password1
            db.session.add(user)
            db.session.delete(token)
            db.session.commit()
            flask.flash(messages.PASSWORD_UPDATE_SUCCESS, category="success")
            return flask.redirect(flask.url_for(".login"))

    return flask.render_template("reset_password.html", form=form, jwt=jwt)
