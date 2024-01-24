import flask
import flask_login

from .. import forms


__all__ = (
    "logout",
)


@flask_login.login_required
def logout():
    form = forms.Logout()
    if form.validate_on_submit():
        flask_login.logout_user()
    return flask.redirect(flask.url_for(".login"))
