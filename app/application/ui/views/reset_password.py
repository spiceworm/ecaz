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
    if form.validate_on_submit():
        token = ApiToken.query.filter(ApiToken.value == jwt).one_or_none()

        password1 = form.password1.data
        password2 = form.password2.data
        if password1 == password2:
            user = token.user
            user.password_hash = flask.g.bcrypt.generate_password_hash(password1).decode("utf-8")
            db.session.add(user)
            db.session.commit()
            flask.flash(messages.PASSWORD_UPDATE_SUCCESS, category="success")
            return flask.redirect(flask.url_for(".login"))
        else:
            flask.flash(messages.PASSWORD_UPDATE_MATCH_ERROR, category="error")
    return flask.render_template("reset_password.html", form=form, jwt=jwt)
