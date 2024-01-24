import flask
from flask_jwt_extended import create_access_token
import flask_login


from .. import forms
from ...models import (
    ApiToken,
    db,
)


__all__ = (
    "api_settings",
    "create_api_token",
    "delete_api_token",
)


@flask_login.login_required
def api_settings():
    return flask.render_template(
        "api_settings.html",
        create_api_token_form=forms.CreateApiToken(),
        delete_api_token_form=forms.DeleteApiToken(),
        logout_form=forms.Logout(),
    )


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
    return flask.redirect(flask.url_for(".api_settings"))


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
    return flask.redirect(flask.url_for(".api_settings"))
