import flask
from flask_jwt_extended import create_access_token
import flask_login


from .. import forms
from ...models import (
    ApiToken,
    db,
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
            flask.flash("Passwords updated successfully")
        else:
            flask.flash("Passwords must match")
    return flask.redirect(flask.url_for(".profile"))


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


@flask_login.login_required
def logout():
    form = forms.Logout()
    if form.validate_on_submit():
        flask_login.logout_user()
    return flask.redirect(flask.url_for(".login"))


@flask_login.login_required
def profile():
    return flask.render_template(
        "profile.html",
        change_password_form=forms.ChangePassword(),
        create_api_token_form=forms.CreateApiToken(),
        delete_api_token_form=forms.DeleteApiToken(),
        logout_form=forms.Logout(),
    )
