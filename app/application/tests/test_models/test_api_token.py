from datetime import timedelta
import time

import pytest

from application.models import ApiToken


def test_create(user):
    """
    Verify attributes of ApiToken instance.
    """
    name = "token"
    u = user()
    token = ApiToken.create(name=name, user=u)
    assert token.name == name
    assert token.user is u
    assert len(token.value) > 0


@pytest.mark.parametrize("method, tag", [
    (ApiToken.create_email_verification_token, ApiToken.VERIFY_EMAIL_TAG),
    (ApiToken.create_frontend_token, ApiToken.FRONTEND_TAG),
    (ApiToken.create_reset_password_token, ApiToken.RESET_PASSWORD_TAG),
    (ApiToken.create_mfa_totp_token, ApiToken.TOTP_MFA_TAG),
    (ApiToken.create_mfa_webauthn_token, ApiToken.WEBAUTHN_MFA_TAG),
])
def test_action_specific_tokens(user, method, tag):
    """
    Verify attributes of ApiToken instance used for specific operations.
    """
    u = user()
    token = method(u)
    assert token.user is u
    assert token.name == tag
    assert token.tags == [ApiToken.HIDDEN_TAG, tag]


def test_is_expired(user):
    """
    Verify `ApiToken.is_expired` attribute behavior for a token with an expiration.
    """
    u = user()
    token1 = ApiToken.create(name="t1", user=u, expires_delta=timedelta(microseconds=1))
    token2 = ApiToken.create(name="t2", user=u, expires_delta=timedelta(days=1))
    time.sleep(0.0000011)
    assert token1.is_expired
    assert not token2.is_expired


def test_is_expired_if_never_expires(user):
    """
    Verify `ApiToken.is_expired` attribute behavior for a token without an expiration.
    """
    u = user()
    token = ApiToken.create(name="t", user=u)
    assert token.is_expired is False


def test_tags_when_token_expired(user):
    """
    Verify `ApiToken.tags` attribute behavior when token is expired.
    """
    token = ApiToken.create_email_verification_token(
        user(),
        timedelta(microseconds=1),
    )
    time.sleep(0.0000011)
    assert token.tags == []
