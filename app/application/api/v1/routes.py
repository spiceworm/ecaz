from flask import (
    Blueprint,
    jsonify,
)
from flask_jwt_extended import (
    get_jwt_identity,
    jwt_required,
)


api_v1_bp = Blueprint(
    "api_v1_bp",
    __name__,
    url_prefix="/v1",
)


@api_v1_bp.route("status")
def status():
    return {"message": "ok"}


@api_v1_bp.route("user")
@jwt_required()
def user():
    return jsonify(logged_in_as=get_jwt_identity())
