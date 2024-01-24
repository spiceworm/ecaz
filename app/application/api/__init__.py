import flask

from .v1.routes import api_v1_bp

api_bp = flask.Blueprint(
    "api_bp",
    __name__,
    url_prefix="/api",
)
api_bp.register_blueprint(api_v1_bp)
