import pytest

from application.models import (
    AuthToken,
    db,
)


@pytest.mark.parametrize(
    "attr_name, exp_value",
    (
        ("is_admin", False),
        ("is_banned", False),
        ("is_deleted", False),
        ("is_verified", False),
    ),
)
def test_defaults(user, attr_name, exp_value):
    """
    Test `User` instance default attribute values.
    """
    u = user()
    assert getattr(u, attr_name) == exp_value


def test_frontend_tokens(user):
    """
    Test that each call to `User.frontend_token` returns a new `AuthToken` instance
    with the `AuthToken.FRONTEND_TAG`.
    """
    u = user()
    t1 = u.frontend_token
    t1_value = t1.value
    assert AuthToken.FRONTEND_TAG in t1.tags
    t2 = u.frontend_token
    t2_value = t2.value
    assert AuthToken.FRONTEND_TAG in t1.tags
    assert t1_value != t2_value


def test_public_auth_tokens(auth_token, user):
    """
    Test `User.auth_tokens` attribute excludes `AuthToken`s that have the
    `AuthToken.HIDDEN_TAG` in its claims.
    """
    u = user()
    auth_token(name="t1", user=u, tags=[AuthToken.HIDDEN_TAG])
    auth_token(name="t2", user=u, tags=[AuthToken.HIDDEN_TAG])
    auth_token(name="t3", user=u, tags=[AuthToken.HIDDEN_TAG])
    db.session.commit()
    assert u.public_auth_tokens == []

    t4 = auth_token(name="t4", user=u)
    t5 = auth_token(name="t5", user=u)
    t6 = auth_token(name="t6", user=u)
    db.session.commit()
    assert u.public_auth_tokens == [t4, t5, t6]
