import flask
import flask_login


from .. import forms
from ...models import db


__all__ = (
    "change_password",
    "settings",
)


@flask_login.login_required
def change_password():
    form = forms.ChangePassword()
    if form.validate_on_submit():
        password1 = form.password1.data
        password2 = form.password2.data
        if password1 == password2:
            user = flask_login.current_user
            user.password_hash = flask.g.bcrypt.generate_password_hash(password1).decode("utf-8")
            db.session.add(user)
            db.session.commit()
            flask.flash("Password updated", category="success")
        else:
            flask.flash("Passwords must match", category="error")
    return flask.redirect(flask.url_for(".settings"))


@flask_login.login_required
def settings():
    return flask.render_template(
        "settings.html",
        change_password_form=forms.ChangePassword(),
        logout_form=forms.Logout(),
    )
