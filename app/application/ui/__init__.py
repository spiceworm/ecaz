import flask

from application.ui import views


ui_bp = flask.Blueprint(
    "ui_bp",
    __name__,
    template_folder="templates",
    static_folder="/static",
    static_url_path="/static",
)

GET = "GET"
POST = "POST"

ui_bp.add_url_rule("/", view_func=views.login, methods=[GET, POST])
ui_bp.add_url_rule("/discussion/topics", view_func=views.view_topics, methods=[GET])
ui_bp.add_url_rule("/discussion/topics/<topic>", view_func=views.view_topic, methods=[GET])
ui_bp.add_url_rule("/discussion/topics/<topic>/<thread_unique_id>/<slug>", view_func=views.view_thread, methods=[GET])
ui_bp.add_url_rule("/discussion/topic", view_func=views.create_topic, methods=[GET, POST])
ui_bp.add_url_rule("/discussion/topic/<topic>", view_func=views.create_thread, methods=[GET, POST])
ui_bp.add_url_rule(
    "/discussion/topic/<topic>/<thread_unique_id>/<slug>/<parent_unique_id>",
    view_func=views.create_comment,
    methods=[POST],
)
ui_bp.add_url_rule("/error", view_func=views.error, methods=[GET])
ui_bp.add_url_rule("/forgot_password", view_func=views.forgot_password, methods=[GET, POST])
ui_bp.add_url_rule("/login", view_func=views.login, methods=[GET, POST])
ui_bp.add_url_rule("/login/mfa/totp/<jwt>", view_func=views.totp_login, methods=[GET, POST])
ui_bp.add_url_rule("/login/mfa/webauthn/<jwt>", view_func=views.webauthn_login, methods=[GET, POST])
ui_bp.add_url_rule("/logout", view_func=views.logout, methods=[POST])
ui_bp.add_url_rule("/register", view_func=views.register, methods=[GET, POST])
ui_bp.add_url_rule("/reset_password/<jwt>", view_func=views.reset_password, methods=[GET, POST])
ui_bp.add_url_rule("/profile", view_func=views.profile, methods=[GET])
ui_bp.add_url_rule("/settings", view_func=views.settings, methods=[GET])
ui_bp.add_url_rule("/settings/auth_token", view_func=views.auth_token_settings, methods=[GET])
ui_bp.add_url_rule("/settings/auth_token/create", view_func=views.create_auth_token, methods=[POST])
ui_bp.add_url_rule("/settings/auth_token/delete", view_func=views.delete_auth_token, methods=[POST])
ui_bp.add_url_rule("/settings/user/email/verify", view_func=views.send_verify_email, methods=[POST])
ui_bp.add_url_rule("/settings/user/email/verify/<jwt>", view_func=views.verify_email, methods=[GET])
ui_bp.add_url_rule("/settings/user/password", view_func=views.change_password, methods=[POST])
ui_bp.add_url_rule("/settings/user/username", view_func=views.change_username, methods=[POST])
ui_bp.add_url_rule("/settings/account/delete", view_func=views.delete_account, methods=[POST])
ui_bp.add_url_rule("/settings/mfa/totp/disable", view_func=views.disable_totp, methods=[POST])
ui_bp.add_url_rule("/settings/mfa/totp/setup", view_func=views.setup_totp, methods=[GET, POST])
ui_bp.add_url_rule("/settings/mfa/webauthn/disable", view_func=views.disable_webauthn, methods=[POST])
ui_bp.add_url_rule("/settings/mfa/webauthn/setup", view_func=views.setup_webauthn, methods=[GET, POST])
