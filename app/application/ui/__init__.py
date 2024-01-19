import collections

import flask

from application.ui import views


ui_bp = flask.Blueprint(
    "ui_bp",
    __name__,
    template_folder="templates",
    static_folder="/static",
    static_url_path="/static",
)

Route = collections.namedtuple("Route", ["rule", "view_func", "methods"])
GET = "GET"
POST = "POST"

for route in [
    Route("/", views.login, [GET, POST]),
    Route("/forgot_password", views.forgot_password, [GET, POST]),
    Route("/login", views.login, [GET, POST]),
    Route("/login/mfa/totp/<jwt>", views.totp_login, [GET, POST]),
    Route("/login/mfa/webauthn/<jwt>", views.webauthn_login, [GET, POST]),
    Route("/logout", views.logout, [POST]),
    Route("/register", views.register, [GET, POST]),
    Route("/reset_password/<jwt>", views.reset_password, [GET, POST]),
    Route("/profile", views.profile, [GET]),
    Route("/settings", views.settings, [GET]),
    Route("/settings/auth_token", views.auth_token_settings, [GET]),
    Route("/settings/auth_token/create", views.create_auth_token, [POST]),
    Route("/settings/auth_token/delete", views.delete_auth_token, [POST]),
    Route("/settings/user/email/verify", views.send_verify_email, [POST]),
    Route("/settings/user/email/verify/<jwt>", views.verify_email, [GET]),
    Route("/settings/user/password", views.change_password, [POST]),
    Route("/settings/user/username", views.change_username, [POST]),
    Route("/settings/account/delete", views.delete_account, [POST]),
    Route("/settings/mfa/totp/disable", views.disable_totp, [POST]),
    Route("/settings/mfa/totp/setup", views.setup_totp, [GET, POST]),
    Route("/settings/mfa/webauthn/disable", views.disable_webauthn, [POST]),
    Route("/settings/mfa/webauthn/setup", views.setup_webauthn, [GET, POST]),
]:
    ui_bp.add_url_rule(rule=route.rule, view_func=route.view_func, methods=route.methods)
