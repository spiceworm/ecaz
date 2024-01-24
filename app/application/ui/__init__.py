from flask import Blueprint

from . import routes


ui_bp = Blueprint(
    "ui_bp",
    __name__,
    template_folder="templates",
    static_folder="static",
    static_url_path="/static",
)

ui_bp.add_url_rule("/", view_func=routes.login, methods=["GET", "POST"])
ui_bp.add_url_rule("/api_settings", view_func=routes.api_settings, methods=["GET"])
ui_bp.add_url_rule("/change_password", view_func=routes.change_password, methods=["POST"])
ui_bp.add_url_rule("/create_api_token", view_func=routes.create_api_token,  methods=["POST"])
ui_bp.add_url_rule("/delete_api_token", view_func=routes.delete_api_token, methods=["POST"])
ui_bp.add_url_rule("/login", view_func=routes.login, methods=["GET", "POST"])
ui_bp.add_url_rule("/logout", view_func=routes.logout, methods=["POST"])
ui_bp.add_url_rule("/profile", view_func=routes.profile, methods=["GET"])
ui_bp.add_url_rule("/register", view_func=routes.register, methods=["GET", "POST"])
ui_bp.add_url_rule("/settings", view_func=routes.settings, methods=["GET"])
