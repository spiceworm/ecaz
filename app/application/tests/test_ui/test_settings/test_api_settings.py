from datetime import timedelta

from application.ui.forms import CreateApiTokenForm


def test_create_api_token(ui_user):
    """
    Verify /api_settings/create_api_token form submission.
    """
    user = ui_user()
    token_name = "test-token-1"
    assert len(user.api_tokens) == 0
    user.post("/settings/api/token/create", data={"token_name": token_name})
    assert len(user.api_tokens) == 1
    assert user.api_tokens[0].name == token_name


def test_create_expiring_api_token(ui_user):
    """
    Verify /api_settings/create_api_token form submission for an expiring token.
    """
    user = ui_user()
    token_name = "test-token-1"
    assert len(user.api_tokens) == 0
    resp = user.post(
        "/settings/api/token/create",
        data={
            "expires_number": "1",
            "expires_unit": CreateApiTokenForm.EXPIRES_UNIT_DAYS,
            "token_name": token_name,
        },
    )
    assert len(user.api_tokens) == 1
    token = user.api_tokens[0]
    assert token.name == token_name
    assert timedelta(hours=23, minutes=59) < token.expires_in < timedelta(days=1, seconds=1)


def test_delete_api_token(ui_user):
    """
    Verify /api_settings/delete_api_token form submission.
    """
    user = ui_user()
    token_name = "test-token-1"
    assert len(user.api_tokens) == 0
    user.post("/settings/api/token/create", data={"token_name": token_name})
    assert len(user.api_tokens) == 1
    user.post("/settings/api/token/delete", data={"id": user.api_tokens[0].id})
    assert len(user.api_tokens) == 0
