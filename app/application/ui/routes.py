import flask
import flask_login


from . import (
    forms,
    ui_bp,
)
from ..models import db, User


@ui_bp.route("/logout", methods=["GET"])
@flask_login.login_required
def logout():
    flask_login.logout_user()
    return flask.url_for(".login")


@ui_bp.route("/profile", methods=["GET"])
@flask_login.login_required
def profile():
    return flask.render_template("profile.html")


@ui_bp.route("/", methods=["GET", "POST"])
@ui_bp.route("/login", methods=["GET", "POST"])
def login():
    form = forms.Login()
    if form.validate_on_submit():
        user = User.query.filter_by(
            password=form.password.data,
            username=form.username.data,
        ).first()
        flask_login.login_user(user)
        nxt = flask.request.args.get("next")
        return flask.redirect(nxt or flask.url_for(".profile"))
    return flask.render_template("login.html", form=form)


@ui_bp.route("/register", methods=["GET", "POST"])
def register():
    form = forms.Register()
    if form.validate_on_submit():
        user = User(
            username=form.username.data,
            password=form.password.data,
        )
        db.session.add(user)
        db.session.commit()
        flask.flash("Registration successful. Please sign in.")
        return flask.render_template("login.html", form=forms.Login())
    return flask.render_template("register.html", form=form)
