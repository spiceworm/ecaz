import flask
import flask_login


from .. import forms


__all__ = (
    "profile",
)


@flask_login.login_required
def profile():
    return flask.render_template(
        "profile.html",
        change_password_form=forms.ChangePassword(),
        create_api_token_form=forms.CreateApiToken(),
        delete_api_token_form=forms.DeleteApiToken(),
        logout_form=forms.Logout(),
    )
