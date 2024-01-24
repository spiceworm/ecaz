from flask import Blueprint


ui_bp = Blueprint(
    "ui_bp",
    __name__,
    template_folder="templates",
    static_folder="static",
    static_url_path="/static",
)

from . import routes
