import flask

from application.api.v1.discussion import api_discussion_bp
from application.api.v1.misc import api_misc_bp


__all__ = ("api_v1_bp",)


api_v1_bp = flask.Blueprint(
    "api_v1_bp",
    __name__,
    url_prefix="/v1",
)
api_v1_bp.register_blueprint(api_discussion_bp)
api_v1_bp.register_blueprint(api_misc_bp)
