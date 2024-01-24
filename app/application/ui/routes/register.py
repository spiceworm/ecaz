import flask
import flask_login
import psycopg2.errors
from psycopg2.errorcodes import UNIQUE_VIOLATION
import sqlalchemy.exc


from .. import forms
from ...models import (
    db,
    User,
)


def register():
    if flask_login.current_user.is_authenticated:
        return flask.redirect(flask.url_for(".profile"))

    form = forms.Register()
    if form.validate_on_submit():
        password_hash = flask.g.bcrypt.generate_password_hash(form.password.data).decode("utf-8")
        user = User(
            username=form.username.data,
            password_hash=password_hash,
        )
        db.session.add(user)
        try:
            db.session.commit()
        except sqlalchemy.exc.IntegrityError as e:
            if isinstance(e.orig, psycopg2.errors.lookup(UNIQUE_VIOLATION)):
                flask.flash("Username already taken")
            else:
                raise e
        else:
            flask_login.login_user(user)
            return flask.redirect(flask.url_for(".profile"))
    return flask.render_template("register.html", form=form)
