def test_create_api_token(ui_user):
    """
    Verify /api_settings/create_api_token form submission.
    """
    user = ui_user()
    token_name = "test-token-1"
    assert len(user.api_tokens) == 0
    user.post("/api_settings/create_api_token", data={"token_name": token_name})
    assert len(user.api_tokens) == 1
    assert user.api_tokens[0].name == token_name


def test_delete_api_token(ui_user):
    """
    Verify /api_settings/delete_api_token form submission.
    """
    user = ui_user()
    token_name = "test-token-1"
    assert len(user.api_tokens) == 0
    user.post("/api_settings/create_api_token", data={"token_name": token_name})
    assert len(user.api_tokens) == 1
    user.post("/api_settings/delete_api_token", data={"id": user.api_tokens[0].id})
    assert len(user.api_tokens) == 0
