from flask import (
    Blueprint,
    jsonify,
)
import flask_restful
from flask_jwt_extended import (
    get_jwt_identity,
    jwt_required,
)


api_v1_bp = Blueprint(
    "api_v1_bp",
    __name__,
    url_prefix="/v1",
)


class StatusApi(flask_restful.Resource):
    def get(self):
        return {"message": "ok"}


class UserApi(flask_restful.Resource):
    @jwt_required()
    def get(self):
        return jsonify(logged_in_as=get_jwt_identity())


api = flask_restful.Api(api_v1_bp)
api.add_resource(StatusApi, '/status')
api.add_resource(UserApi, '/user')
