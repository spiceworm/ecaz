from flask import (
    Blueprint,
    render_template,
)

ui_bp = Blueprint(
    "ui_bp",
    __name__,
    template_folder="templates",
    static_folder="static",
    static_url_path="/static",
)


@ui_bp.route("/")
@ui_bp.route("/index/<value>")
def index(value=""):
    return render_template("index.html", value=value)
