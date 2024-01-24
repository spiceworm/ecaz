import flask
import flask_login

from .. import forms
from ... import util
from ...models import User


def login():
    if flask_login.current_user.is_authenticated:
        return flask.redirect(flask.url_for(".profile"))

    form = forms.Login()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).one_or_none()
        if user is not None:
            is_correct_password = flask.g.bcrypt.check_password_hash(
                user.password_hash,
                form.password.data,
            )
            if is_correct_password:
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

        flask.flash("Invalid login credentials")
    return flask.render_template("login.html", form=form)
