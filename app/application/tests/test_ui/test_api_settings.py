from application.constants import messages
from application.models import (
    ApiToken,
    User,
)


def test_create_api_token(ui_user):
    user = ui_user()
    token_name = "test-token-1"
    assert len(user.api_tokens) == 0
    user.post("/api_settings/create_api_token", data={"token_name": token_name})
    assert len(user.api_tokens) == 1
    assert user.api_tokens[0].name == token_name


def test_delete_account(ui_user):
    user = ui_user()
    resp = user.post("/settings/delete_account", follow_redirects=True)
    assert messages.DELETE_ACCOUNT_SUCCESS in resp.data.decode()
    assert User.query.filter_by(email=user.email).one_or_none() is None
    assert len(resp.history) == 1
    assert resp.request.path == "/"


def test_delete_account_cascades(ui_user):
    user = ui_user()
    token_name = "test-token"
    user.post("/api_settings/create_api_token", data={"token_name": token_name})
    user.post("/settings/delete_account")
    assert User.query.filter_by(email=user.email).one_or_none() is None
    assert ApiToken.query.filter_by(name=token_name).one_or_none() is None


def test_delete_api_token(ui_user):
    user = ui_user()
    token_name = "test-token-1"
    assert len(user.api_tokens) == 0
    user.post("/api_settings/create_api_token", data={"token_name": token_name})
    assert len(user.api_tokens) == 1
    user.post("/api_settings/delete_api_token", data={"id": user.api_tokens[0].id})
    assert len(user.api_tokens) == 0
