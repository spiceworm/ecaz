import json

import webauthn

from application.constants import messages


def test_setup_if_webauthn_already_enabled(ui_user):
    """
    Verify the correct error message is shown if a user attempts to navigate to
    the WebAuthn MFA setup page when it is already enabled for that user.
    """
    user = ui_user()
    user.webauthn.enabled = True
    resp = user.get(
        "/settings/mfa/webauthn/setup",
        follow_redirects=True,
    )
    assert messages.WEBAUTHN_ALREADY_ENABLED in resp.data.decode()
    assert len(resp.history) == 1
    assert resp.request.path == "/settings"


def test_setup_with_invalid_webauthn_options(ui_user):
    """
    Verify the correct error message is shown if a user tries to setup WebAuthn
    MFA using invalid credential creation options. This example is POSTs invalid
    options because the origin in clientDataJSON is not valid.
    """
    user = ui_user()
    credential_creation_options = {
        "id": "ZoIKP1JQvKdrYj1bTUPJ2eTUsbLeFkv-X5xJQNr4k6s",
        "rawId": "ZoIKP1JQvKdrYj1bTUPJ2eTUsbLeFkv-X5xJQNr4k6s",
        "response": {
            "attestationObject": "o2NmbXRkbm9uZWdhdHRTdG10oGhhdXRoRGF0YVkBZ0mWDeWIDoxodDQXD2R2YFuP5K65ooYyx5lc87qDHZdjRQAAAAAAAAAAAAAAAAAAAAAAAAAAACBmggo_UlC8p2tiPVtNQ8nZ5NSxst4WS_5fnElA2viTq6QBAwM5AQAgWQEA31dtHqc70D_h7XHQ6V_nBs3Tscu91kBL7FOw56_VFiaKYRH6Z4KLr4J0S12hFJ_3fBxpKfxyMfK66ZMeAVbOl_wemY4S5Xs4yHSWy21Xm_dgWhLJjZ9R1tjfV49kDPHB_ssdvP7wo3_NmoUPYMgK-edgZ_ehttp_I6hUUCnVaTvn_m76b2j9yEPReSwl-wlGsabYG6INUhTuhSOqG-UpVVQdNJVV7GmIPHCA2cQpJBDZBohT4MBGme_feUgm4sgqVCWzKk6CzIKIz5AIVnspLbu05SulAVnSTB3NxTwCLNJR_9v9oSkvphiNbmQBVQH1tV_psyi9HM1Jtj9VJVKMeyFDAQAB",
            "clientDataJSON": webauthn.helpers.bytes_to_base64url(
                b'{"type":"webauthn.create","challenge":"'
                + webauthn.helpers.bytes_to_base64url(user.webauthn.challenge).encode()
                + b'","origin":"http://invalid-origin","crossOrigin":false}'
            ),
            "transports": ["internal"],
        },
        "type": "public-key",
        "clientExtensionResults": {},
        "authenticatorAttachment": "platform",
    }
    resp = user.post(
        "/settings/mfa/webauthn/setup",
        data={"credential_creation_options": json.dumps(credential_creation_options)},
        follow_redirects=True,
    )
    assert not user.webauthn.enabled
    assert messages.WEBAUTHN_SETUP_VERIFICATION_ERROR in resp.data.decode()
    assert len(resp.history) == 0
    assert resp.request.path == "/settings/mfa/webauthn/setup"


def test_setup_with_valid_webauthn_device(ui_user):
    """
    Verify the correct success message is shown if a user successfully sets
    up TOTP MFA.
    """
    user = ui_user()
    credential_creation_options = {
        "id": "ZoIKP1JQvKdrYj1bTUPJ2eTUsbLeFkv-X5xJQNr4k6s",
        "rawId": "ZoIKP1JQvKdrYj1bTUPJ2eTUsbLeFkv-X5xJQNr4k6s",
        "response": {
            "attestationObject": "o2NmbXRkbm9uZWdhdHRTdG10oGhhdXRoRGF0YVkBZ0mWDeWIDoxodDQXD2R2YFuP5K65ooYyx5lc87qDHZdjRQAAAAAAAAAAAAAAAAAAAAAAAAAAACBmggo_UlC8p2tiPVtNQ8nZ5NSxst4WS_5fnElA2viTq6QBAwM5AQAgWQEA31dtHqc70D_h7XHQ6V_nBs3Tscu91kBL7FOw56_VFiaKYRH6Z4KLr4J0S12hFJ_3fBxpKfxyMfK66ZMeAVbOl_wemY4S5Xs4yHSWy21Xm_dgWhLJjZ9R1tjfV49kDPHB_ssdvP7wo3_NmoUPYMgK-edgZ_ehttp_I6hUUCnVaTvn_m76b2j9yEPReSwl-wlGsabYG6INUhTuhSOqG-UpVVQdNJVV7GmIPHCA2cQpJBDZBohT4MBGme_feUgm4sgqVCWzKk6CzIKIz5AIVnspLbu05SulAVnSTB3NxTwCLNJR_9v9oSkvphiNbmQBVQH1tV_psyi9HM1Jtj9VJVKMeyFDAQAB",
            "clientDataJSON": webauthn.helpers.bytes_to_base64url(
                b'{"type":"webauthn.create","challenge":"'
                + webauthn.helpers.bytes_to_base64url(user.webauthn.challenge).encode()
                + b'","origin":"http://localhost","crossOrigin":false}'
            ),
            "transports": ["internal"],
        },
        "type": "public-key",
        "clientExtensionResults": {},
        "authenticatorAttachment": "platform",
    }
    resp = user.post(
        "/settings/mfa/webauthn/setup",
        data={"credential_creation_options": json.dumps(credential_creation_options)},
        follow_redirects=True,
    )
    # print(resp.data.decode())
    assert user.webauthn.enabled
    assert messages.WEBAUTHN_SETUP_VERIFICATION_SUCCESS in resp.data.decode()
    assert len(resp.history) == 1
    assert resp.request.path == "/settings"
