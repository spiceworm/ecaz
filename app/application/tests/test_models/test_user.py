import pytest

from application.models import (
    ApiToken,
    db,
)


@pytest.mark.parametrize("attr_name, exp_value", (
    ("is_admin", False),
    ("is_banned", False),
    ("is_deleted", False),
    ("is_verified", False),
))
def test_defaults(user, attr_name, exp_value):
    u = user()
    assert getattr(u, attr_name) == exp_value


def test_public_api_tokens(api_token, user):
    u = user()
    api_token(name="t1", user=u, tags=[ApiToken.HIDDEN_TAG])
    api_token(name="t2", user=u, tags=[ApiToken.HIDDEN_TAG])
    api_token(name="t3", user=u, tags=[ApiToken.HIDDEN_TAG])
    db.session.commit()
    assert u.public_api_tokens == []

    t4 = api_token(name="t4", user=u)
    t5 = api_token(name="t5", user=u)
    t6 = api_token(name="t6", user=u)
    db.session.commit()
    assert u.public_api_tokens == [t4, t5, t6]
