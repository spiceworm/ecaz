import flask
import flask_login

from application.ui import forms


__all__ = ("profile",)


@flask_login.login_required
def profile() -> str:
    return flask.render_template(
        "profile.html",
        logout_form=forms.LogoutForm(),
    )
