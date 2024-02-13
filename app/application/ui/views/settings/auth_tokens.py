import datetime

import flask
import flask_login
from werkzeug.wrappers import Response

from application.constants import expires
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
        expires_at_unit = form.expires_at_unit.data
        if expires_at_unit == expires.NEVER:
            expires_delta = False
        else:
            expires_delta = datetime.timedelta(**{expires_at_unit.lower(): int(form.expires_at_number.data)})

        AuthToken.create(
            user=user,
            name=form.token_name.data,
            expires_delta=expires_delta,
        )
    return flask.redirect(flask.url_for("ui_bp.auth_token_settings"))


@flask_login.login_required
def delete_auth_token() -> Response:
    form = forms.DeleteAuthTokenForm()
    if form.validate_on_submit():
        AuthToken.query.filter(
            AuthToken.id == form.id.data,
            AuthToken.user_id == flask_login.current_user.id,
        ).delete()
        db.session.commit()
    return flask.redirect(flask.url_for("ui_bp.auth_token_settings"))
