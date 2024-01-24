import flask

from . import views


ui_bp = flask.Blueprint(
    "ui_bp",
    __name__,
    template_folder="templates",
    static_folder="static",
    static_url_path="/static",
)

ui_bp.add_url_rule("/", view_func=views.login, methods=["GET", "POST"])
ui_bp.add_url_rule("/login", view_func=views.login, methods=["GET", "POST"])
ui_bp.add_url_rule("/logout", view_func=views.logout, methods=["POST"])
ui_bp.add_url_rule("/profile", view_func=views.profile, methods=["GET"])

ui_bp.add_url_rule("/api_settings", view_func=views.api_settings, methods=["GET"])
ui_bp.add_url_rule(
    "/api_settings/create_api_token", view_func=views.create_api_token, methods=["POST"]
)
ui_bp.add_url_rule(
    "/api_settings/delete_api_token", view_func=views.delete_api_token, methods=["POST"]
)

ui_bp.add_url_rule("/forgot_password", view_func=views.forgot_password, methods=["GET", "POST"])
ui_bp.add_url_rule("/reset_password/<jwt>", view_func=views.reset_password, methods=["GET", "POST"])

ui_bp.add_url_rule("/register", view_func=views.register, methods=["GET", "POST"])

ui_bp.add_url_rule("/settings", view_func=views.settings, methods=["GET"])
ui_bp.add_url_rule("/settings/change_password", view_func=views.change_password, methods=["POST"])
ui_bp.add_url_rule("/settings/change_username", view_func=views.change_username, methods=["POST"])
ui_bp.add_url_rule("/settings/delete_account", view_func=views.delete_account, methods=["POST"])
ui_bp.add_url_rule("/settings/verify", view_func=views.send_verify_email, methods=["POST"])
ui_bp.add_url_rule("/settings/verify/<jwt>", view_func=views.verify_account, methods=["GET"])
