from datetime import timedelta
import time

from application.models import ApiToken


def test_create(user):
    name = "token"
    u = user()
    token = ApiToken.create(name=name, user=u)
    assert token.name == name
    assert token.user is u
    assert len(token.value) > 0


def test_create_email_verification_token(user):
    u = user()
    token = ApiToken.create_email_verification_token(u)
    assert token.user is u
    assert token.name == ApiToken.VERIFY_EMAIL_TAG
    assert token.tags == [ApiToken.HIDDEN_TAG, ApiToken.VERIFY_EMAIL_TAG]


def test_create_reset_password_token(user):
    u = user()
    token = ApiToken.create_reset_password_token(u)
    assert token.user is u
    assert token.name == ApiToken.RESET_PASSWORD_TAG
    assert token.tags == [ApiToken.HIDDEN_TAG, ApiToken.RESET_PASSWORD_TAG]


def test_is_expired(user):
    u = user()
    token1 = ApiToken.create(name="t1", user=u, expires_delta=timedelta(microseconds=1))
    token2 = ApiToken.create(name="t2", user=u, expires_delta=timedelta(days=1))
    time.sleep(0.0000011)
    assert token1.is_expired
    assert not token2.is_expired
