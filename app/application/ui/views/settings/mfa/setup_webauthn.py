import flask
import flask_login
import webauthn
from webauthn.helpers.exceptions import InvalidRegistrationResponse

from application.constants import messages
from application.models import db
from application.ui import forms


__all__ = (
    "setup_webauthn",
)


@flask_login.login_required
def setup_webauthn():
    user = flask_login.current_user
    form = forms.SetupWebauthnForm()
    if form.validate_on_submit():
        try:
            registration = webauthn.verify_registration_response(
                credential=form.credential_creation_options.data,
                expected_challenge=user.webauthn.challenge,
                expected_origin=flask.g.config.BASE_URL,
                expected_rp_id=flask.g.config.APP_NAME,
            )
        except InvalidRegistrationResponse as e:
            flask.flash(messages.WEBAUTHN_SETUP_VERIFICATION_ERROR + f": {e}", category="error")
        else:
            registrations = user.webauthn.registrations
            registrations.append({
                "id": registration.credential_id,
                "type": registration.credential_type.value,
            })
            user.webauthn.registrations = registrations
            user.webauthn.public_key = registration.credential_public_key
            user.webauthn.enabled = True
            db.session.add(user)
            db.session.commit()
            flask.flash(messages.WEBAUTHN_SETUP_VERIFICATION_SUCCESS)
            return flask.redirect(flask.url_for(".settings"))

    registration_options = webauthn.options_to_json(
        webauthn.generate_registration_options(
            challenge=user.webauthn.challenge,
            exclude_credentials=user.webauthn.registrations,
            rp_id=flask.g.config.APP_NAME,
            rp_name=flask.g.config.APP_NAME,
            user_name=user.email,
            user_id=user.webauthn.user_handle,
        )
    )

    return flask.render_template(
        "settings/mfa/setup_webauthn.html",
        form=form,
        logout_form=forms.LogoutForm(),
        registration_options=registration_options,
    )
