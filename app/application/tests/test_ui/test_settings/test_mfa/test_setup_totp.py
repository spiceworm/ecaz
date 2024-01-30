from flask import url_for

from application.constants import messages


def test_setup_if_totp_already_enabled(ui_user):
    """
    Verify the correct error message is shown if a user attempts to navigate to
    the TOTP MFA setup page when it is already enabled for that user.
    """
    user = ui_user()
    user.mfa.totp.enabled = True
    resp = user.get(
        url_for("ui_bp.setup_totp"),
        follow_redirects=True,
    )
    assert messages.TOTP_ALREADY_ENABLED in resp.data.decode()
    assert len(resp.history) == 1
    assert resp.request.base_url == url_for("ui_bp.settings")


def test_setup_with_invalid_totp_code(ui_user):
    """
    Verify the correct error message is shown if a user tries to setup TOTP
    MFA using a bad setup code.
    """
    user = ui_user()
    totp_code = int(user.mfa.totp.handler.now()) + 1
    resp = user.post(
        url_for("ui_bp.setup_totp"),
        data={"totp_code": str(totp_code)},
        follow_redirects=True,
    )
    assert not user.mfa.totp.enabled
    assert messages.TOTP_SETUP_VERIFICATION_ERROR in resp.data.decode()
    assert len(resp.history) == 0
    assert resp.request.base_url == url_for("ui_bp.setup_totp")


def test_setup_with_valid_totp_code(ui_user):
    """
    Verify the correct success message is shown if a user successfully sets
    up TOTP MFA.
    """
    user = ui_user()
    resp = user.post(
        url_for("ui_bp.setup_totp"),
        data={"totp_code": user.mfa.totp.handler.now()},
        follow_redirects=True,
    )
    assert user.mfa.totp.enabled
    assert messages.TOTP_SETUP_VERIFICATION_SUCCESS in resp.data.decode()
    assert len(resp.history) == 1
    assert resp.request.base_url == url_for("ui_bp.settings")
