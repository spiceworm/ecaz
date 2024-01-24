import flask
from flask_jwt_extended import create_access_token
import flask_login


from . import (
    forms,
    ui_bp,
)
from ..models import (
    ApiToken,
    db,
    User,
)


@ui_bp.route("/create_api_token", methods=["POST"])
@flask_login.login_required
def create_api_token():
    user = flask_login.current_user
    form = forms.CreateApiToken()
    if form.validate_on_submit():
        token_value = create_access_token(
            expires_delta=False,
            identity=user.username,
        )
        api_token = ApiToken(
            name=form.token_name.data,
            value=token_value,
            user=user,
        )
        db.session.add(api_token)
        db.session.commit()
    return flask.redirect(flask.url_for(".profile"))


@ui_bp.route("/delete_api_token", methods=["POST"])
@flask_login.login_required
def delete_api_token():
    user = flask_login.current_user
    form = forms.DeleteApiToken()
    if form.validate_on_submit():
        ApiToken.query.filter(
            ApiToken.id == form.id.data,
            ApiToken.user_id == user.id,
        ).delete()
        db.session.commit()
    return flask.redirect(flask.url_for(".profile"))


@ui_bp.route("/", methods=["GET", "POST"])
@ui_bp.route("/login", methods=["GET", "POST"])
def login():
    if flask_login.current_user.is_authenticated:
        return flask.redirect(flask.url_for(".profile"))

    form = forms.Login()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user is not None:
            is_correct_password = flask.g.bcrypt.check_password_hash(
                user.password_hash,
                form.password.data,
            )
            if is_correct_password:
                flask_login.login_user(user)
                return flask.redirect(flask.url_for(".profile"))
        flask.flash("Invalid login credentials")
    return flask.render_template("login.html", form=form)


@ui_bp.route("/logout", methods=["POST"])
@flask_login.login_required
def logout():
    form = forms.Logout()
    if form.validate_on_submit():
        flask_login.logout_user()
    return flask.redirect(flask.url_for(".login"))


@ui_bp.route("/profile", methods=["GET"])
@flask_login.login_required
def profile():
    return flask.render_template(
        "profile.html",
        create_api_token_form=forms.CreateApiToken(),
        delete_api_token_form=forms.DeleteApiToken(),
        logout_form=forms.Logout(),
    )


@ui_bp.route("/register", methods=["GET", "POST"])
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
        db.session.commit()
        flask_login.login_user(user)
        return flask.redirect(flask.url_for(".profile"))
    return flask.render_template("register.html", form=form)
