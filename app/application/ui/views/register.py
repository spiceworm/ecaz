import flask
import flask_login
import flask_mailman
import psycopg2.errors
from psycopg2.errorcodes import UNIQUE_VIOLATION
import sqlalchemy.exc

from .. import forms
from ...constants import messages
from ...models import (
    ApiToken,
    db,
    User,
)


__all__ = (
    "register",
)


def register():
    if flask_login.current_user.is_authenticated:
        return flask.redirect(flask.url_for(".profile"))

    form = forms.RegisterForm()
    if form.validate_on_submit():
        user = User(
            email=form.email.data,
            password=form.password.data,
            username=form.email.data,
        )
        db.session.add(user)
        try:
            db.session.commit()
        except sqlalchemy.exc.IntegrityError as e:
            if isinstance(e.orig, psycopg2.errors.lookup(UNIQUE_VIOLATION)):
                db.session.rollback()
                flask.flash(messages.DUPLICATE_EMAIL_ERROR, category="error")
            else:
                raise e
        else:
            flask_login.login_user(user)
            return flask.redirect(flask.url_for(".profile"))
    return flask.render_template("register.html", form=form)
