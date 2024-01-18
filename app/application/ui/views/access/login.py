import flask
import flask_login
import webauthn
from webauthn.helpers.exceptions import InvalidAuthenticationResponse

from application.constants import messages
from application.models import (
    ApiToken,
    db,
    User,
)
from application.third_party.util import url_has_allowed_host_and_scheme
from application.ui import forms


__all__ = (
    "login",
    "totp_login",
    "webauthn_login",
)


def _login(user):
    flask_login.login_user(user)
    next_page = flask.request.args.get("next")

    # If the user was trying to access a login protected page but were not logged in.
    # Prevent open redirection vulnerability.
    if next_page and url_has_allowed_host_and_scheme(next_page, flask.request.host):
        return flask.redirect(next_page)
    else:
        return flask.redirect(flask.url_for(".profile"))


def login():
    if flask_login.current_user.is_authenticated:
        return flask.redirect(flask.url_for(".profile"))

    form = forms.LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).one_or_none()
        if user and user.password == form.password.data:
            if user.is_deleted:
                flask.flash(messages.DELETE_ACCOUNT_PENDING, category="info")
            elif user.webauthn.enabled:
                # WebAuthn MFA supersedes Totp MFA
                webauthn_token = ApiToken.create_mfa_webauthn_token(user)
                return flask.redirect(flask.url_for(".webauthn_login", jwt=webauthn_token.value))
            elif user.totp.enabled:
                totp_token = ApiToken.create_mfa_totp_token(user)
                return flask.redirect(flask.url_for(".totp_login", jwt=totp_token.value))
            else:
                return _login(user)
        else:
            flask.flash(messages.INVALID_LOGIN_ERROR, category="error")
    return flask.render_template("access/login/login.html", form=form)


def totp_login(jwt):
    if flask_login.current_user.is_authenticated:
        return flask.redirect(flask.url_for(".profile"))

    token = ApiToken.query.filter(ApiToken.value == jwt).one_or_none()
    if token and not token.is_expired and ApiToken.TOTP_MFA_TAG in token.tags:
        form = forms.TotpLoginForm()
        if form.validate_on_submit():
            if token.user.totp.verify(form.totp_code.data):
                return _login(token.user)
            else:
                flask.flash(messages.TOTP_CODE_INVALID, category="error")
        return flask.render_template("access/login/totp_login.html", form=form)
    else:
        flask.flash(messages.INVALID_TOKEN, category="error")
        return flask.redirect(flask.url_for(".login"))


def webauthn_login(jwt):
    if flask_login.current_user.is_authenticated:
        return flask.redirect(flask.url_for(".profile"))

    token = ApiToken.query.filter(ApiToken.value == jwt).one_or_none()
    if token and not token.is_expired and ApiToken.WEBAUTHN_MFA_TAG in token.tags:
        user = token.user
        authentication_options = webauthn.options_to_json(
            webauthn.generate_authentication_options(
                rp_id=flask.g.config.APP_NAME,
                challenge=user.webauthn.challenge,
                allow_credentials=user.webauthn.registrations,
            )
        )

        form = forms.WebauthnLoginForm()
        if form.validate_on_submit():
            try:
                authentication = webauthn.verify_authentication_response(
                    credential=form.credential_authentication_options.data,
                    expected_challenge=user.webauthn.challenge,
                    expected_rp_id=flask.g.config.APP_NAME,
                    expected_origin=flask.g.config.BASE_URL,
                    credential_public_key=user.webauthn.public_key,
                    credential_current_sign_count=user.webauthn.credential_sign_count,
                )
            except InvalidAuthenticationResponse as e:
                flask.flash(messages.WEBAUTHN_AUTHENTICATION_ERROR + f": {e}", category="error")
                return flask.redirect(flask.url_for(".login"))
            else:
                user.webauthn.credential_sign_count = authentication.new_sign_count
                db.session.delete(token)
                db.session.add(user)
                db.session.commit()
                return _login(token.user)
        return flask.render_template(
            "access/login/webauth_login.html",
            authentication_options=authentication_options,
            form=form,
        )
    else:
        flask.flash(messages.INVALID_TOKEN, category="error")
        return flask.redirect(flask.url_for(".login"))
