from typing import Union

import flask
import flask_login
from werkzeug.wrappers import Response

from application.models import (
    db,
    User,
)
from application.ui import forms
from application.util.decorators import require_unauthenticated


__all__ = ("register",)


@require_unauthenticated(if_authenticated_redirect_to=".profile")
def register() -> Union[str, Response]:
    form = forms.RegisterForm()
    if form.validate_on_submit():
        user = User(
            email=form.email.data,
            password=form.password.data,
            username=form.username.data,
        )
        db.session.add(user)
        db.session.commit()
        flask_login.login_user(user)
        return flask.redirect(flask.url_for(".profile"))

    return flask.render_template("access/register.html", form=form)
