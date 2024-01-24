import flask
import flask_login
from werkzeug.wrappers import Response

from application.ui import forms


__all__ = ("logout",)


@flask_login.login_required
def logout() -> Response:
    form = forms.LogoutForm()
    if form.validate_on_submit():
        flask_login.logout_user()
    return flask.redirect(flask.url_for(".login"))
