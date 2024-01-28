import flask

from application.ui import forms


__all__ = ("error",)


def error() -> str:
    return flask.render_template(
        "error.html",
        logout_form=forms.LogoutForm(),
    )
