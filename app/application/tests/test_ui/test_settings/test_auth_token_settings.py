from datetime import timedelta

from flask import url_for

from application.constants import expires


def test_create_auth_token(ui_user):
    """
    Verify /api_settings/create_auth_token form submission.
    """
    user = ui_user()
    token_name = "test-token-1"
    assert len(user.auth_tokens) == 0
    user.post(url_for("ui_bp.create_auth_token"), data={"token_name": token_name})
    assert len(user.auth_tokens) == 1
    assert user.auth_tokens[0].name == token_name


def test_create_expiring_auth_token(ui_user):
    """
    Verify /api_settings/create_auth_token form submission for an expiring token.
    """
    user = ui_user()
    token_name = "test-token-1"
    assert len(user.auth_tokens) == 0
    user.post(
        url_for("ui_bp.create_auth_token"),
        data={
            "expires_at_number": "1",
            "expires_at_unit": expires.UNIT_DAYS,
            "token_name": token_name,
        },
    )
    assert len(user.auth_tokens) == 1
    token = user.auth_tokens[0]
    assert token.name == token_name
    assert timedelta(hours=23, minutes=59) < token.expires_at < timedelta(days=1, seconds=1)


def test_delete_auth_token(ui_user):
    """
    Verify /api_settings/delete_auth_token form submission.
    """
    user = ui_user()
    token_name = "test-token-1"
    assert len(user.auth_tokens) == 0
    user.post(url_for("ui_bp.create_auth_token"), data={"token_name": token_name})
    assert len(user.auth_tokens) == 1
    user.post(url_for("ui_bp.delete_auth_token"), data={"id": user.auth_tokens[0].id})
    assert len(user.auth_tokens) == 0
