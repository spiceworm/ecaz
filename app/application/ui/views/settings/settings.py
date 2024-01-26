import flask
import flask_login
from werkzeug.wrappers import Response

from application.constants import messages
from application.models import (
    db,
    Totp,
    WebAuthn,
)
from application.ui import forms


__all__ = (
    "delete_account",
    "disable_totp",
    "disable_webauthn",
    "settings",
)


@flask_login.login_required
def delete_account() -> Response:
    """
    This view could get deleted in the future in favor of marking the user as pending
    for deletion instead of deleting them right away. This would be necessary if there
    were many objects related the user object that also required deletion which could
    cause the client's request to timeout while each object was deleted.
    """
    form = forms.DeleteAccountForm()
    if form.validate_on_submit():
        # Setting this attribute for the future where a deletion queue exists and a job
        # that checks for all user accounts marked for deletion runs periodically.
        flask_login.current_user.is_deleted = True

        db.session.delete(flask_login.current_user)
        db.session.commit()
        flask_login.logout_user()
        flask.flash(messages.DELETE_ACCOUNT_SUCCESS, category="success")
    return flask.redirect(flask.url_for(".login"))


@flask_login.login_required
def disable_totp() -> Response:
    user = flask_login.current_user
    totp = user.mfa.totp
    form = forms.TotpDisableForm()
    if form.validate_on_submit():
        if totp.enabled:
            # Reset Totp instance associated with current user
            db.session.delete(totp)
            db.session.add(Totp(mfa=user.mfa))
            db.session.commit()
            flask.flash(messages.TOTP_NOW_DISABLED)
        else:
            flask.flash(messages.TOTP_NOT_ENABLED, category="info")
    return flask.redirect(flask.url_for(".settings"))


@flask_login.login_required
def disable_webauthn() -> Response:
    user = flask_login.current_user
    _webauthn = user.mfa.webauthn
    form = forms.WebAuthnDisableForm()
    if form.validate_on_submit():
        if _webauthn.enabled:
            # Reset WebAuthn instance associated with current user
            db.session.delete(_webauthn)
            db.session.add(WebAuthn(mfa=user.mfa))
            db.session.commit()
            flask.flash(messages.WEBAUTHN_NOW_DISABLED)
        else:
            flask.flash(messages.WEBAUTHN_NOT_ENABLED, category="info")
    return flask.redirect(flask.url_for(".settings"))


@flask_login.login_required
def settings() -> str:
    return flask.render_template(
        "settings/settings.html",
        change_password_form=forms.ChangePasswordForm(),
        change_username_form=forms.ChangeUsernameForm(),
        delete_account_form=forms.DeleteAccountForm(),
        email_form=forms.EmailForm(),
        logout_form=forms.LogoutForm(),
        totp_disable_form=forms.TotpDisableForm(),
        webauthn_disable_form=forms.WebAuthnDisableForm(),
    )
