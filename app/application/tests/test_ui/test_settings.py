from application.constants import messages


def test_change_password(ui_user):
    user = ui_user()
    resp1 = user.post(
        "/settings/change_password",
        follow_redirects=True,
        data={
            "password1": "new-password",
            "password2": "new-password",
        },
    )
    assert messages.PASSWORD_UPDATE_SUCCESS in resp1.data.decode()
    resp2 = user.post(
        "/settings/change_password",
        follow_redirects=True,
        data={
            "password1": "test-password",
            "password2": "test-password",
        },
    )
    assert messages.PASSWORD_UPDATE_SUCCESS in resp2.data.decode()


def test_change_password_not_matching(ui_user):
    resp = ui_user().post(
        "/settings/change_password",
        follow_redirects=True,
        data={
            "password1": "new-password",
            "password2": "this-does-not-match",
        },
    )
    assert messages.PASSWORD_UPDATE_MATCH_ERROR in resp.data.decode()


def test_change_username(ui_user):
    resp1 = ui_user().post(
        "/settings/change_username",
        follow_redirects=True,
        data={"username": "new-username"},
    )
    assert messages.USERNAME_UPDATE_SUCCESS in resp1.data.decode()
