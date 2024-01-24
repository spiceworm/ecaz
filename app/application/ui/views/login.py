import flask
import flask_login

from .. import forms
from ... import util
from ...constants import messages
from ...models import User


def login():
    if flask_login.current_user.is_authenticated:
        return flask.redirect(flask.url_for(".profile"))

    form = forms.LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).one_or_none()
        if user is not None:
            if user.password == form.password.data:
                if user.is_deleted:
                    flask.flash(messages.DELETE_ACCOUNT_PENDING, category="info")
                else:
                    flask_login.login_user(user)
                    next_page = flask.request.args.get("next")

                    # If the user was trying to access a login protected page but were not logged in.
                    # Prevent open redirection vulnerability.
                    if next_page and util.url_has_allowed_host_and_scheme(
                        next_page, flask.request.host
                    ):
                        return flask.redirect(next_page)
                    else:
                        return flask.redirect(flask.url_for(".profile"))
        else:
            flask.flash(messages.INVALID_LOGIN_ERROR, category="error")
    return flask.render_template("login.html", form=form)
