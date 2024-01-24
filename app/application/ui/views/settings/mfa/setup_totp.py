import flask
import flask_login

from application.constants import messages
from application.models import db
from application.ui import forms


__all__ = (
    "setup_totp",
)


@flask_login.login_required
def setup_totp():
    totp = flask_login.current_user.totp
    if totp.enabled:
        flask.flash(messages.TOTP_ALREADY_ENABLED, category="info")
        return flask.redirect(flask.url_for(".settings"))

    form = forms.SetupTotpForm(setup_secret=totp.secret)
    if form.validate_on_submit():
        if totp.verify(form.totp_code.data):
            totp.enabled = True
            db.session.add(totp)
            db.session.commit()
            flask.flash(messages.TOTP_SETUP_VERIFICATION_SUCCESS)
            return flask.redirect(flask.url_for(".settings"))
        else:
            flask.flash(messages.TOTP_SETUP_VERIFICATION_ERROR, category="error")

    return flask.render_template(
        "settings/mfa/setup_totp.html",
        form=form,
        logout_form=forms.LogoutForm(),
    )
