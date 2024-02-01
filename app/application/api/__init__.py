import flask

from application.api.v1 import api_v1_bp


__all__ = ("api_bp",)


api_bp = flask.Blueprint(
    "api_bp",
    __name__,
    url_prefix="/api",
)
api_bp.register_blueprint(api_v1_bp)
