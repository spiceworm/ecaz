import datetime

import flask
import flask_login
from werkzeug.wrappers import Response

from application.ui import forms
from application.models import (
    AuthToken,
    db,
)


__all__ = (
    "auth_token_settings",
    "create_auth_token",
    "delete_auth_token",
)


@flask_login.login_required
def auth_token_settings() -> str:
    return flask.render_template(
        "settings/auth_tokens.html",
        create_auth_token_form=forms.CreateAuthTokenForm(),
        delete_auth_token_form=forms.DeleteAuthTokenForm(),
        logout_form=forms.LogoutForm(),
    )


@flask_login.login_required
def create_auth_token() -> Response:
    user = flask_login.current_user
    form = forms.CreateAuthTokenForm()
    if form.validate_on_submit():
        expires_unit = form.expires_unit.data
        if expires_unit == form.EXPIRES_NEVER:
            expires_delta = False
        else:
            expires_delta = datetime.timedelta(
                **{expires_unit.lower(): int(form.expires_number.data)}
            )

        token = AuthToken.create(
            user=user,
            name=form.token_name.data,
            expires_delta=expires_delta,
        )
        db.session.add(token)
        db.session.commit()
    return flask.redirect(flask.url_for(".auth_token_settings"))


@flask_login.login_required
def delete_auth_token() -> Response:
    form = forms.DeleteAuthTokenForm()
    if form.validate_on_submit():
        AuthToken.query.filter(
            AuthToken.id == form.id.data,
            AuthToken.user_id == flask_login.current_user.id,
        ).delete()
        db.session.commit()
    return flask.redirect(flask.url_for(".auth_token_settings"))
