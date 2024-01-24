import flask
import flask_login


from .. import forms


__all__ = ("profile",)


@flask_login.login_required
def profile():
    return flask.render_template(
        "profile.html",
        logout_form=forms.LogoutForm(),
    )
