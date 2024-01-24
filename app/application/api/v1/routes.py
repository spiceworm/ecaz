import flask
import flask_mailman
import flask_restful
from flask_jwt_extended import (
    get_jwt_identity,
    jwt_required,
)

from ...models import User


api_v1_bp = flask.Blueprint(
    "api_v1_bp",
    __name__,
    url_prefix="/v1",
)


class EmailApi(flask_restful.Resource):
    @jwt_required()
    def post(self):
        user = User.query.filter(User.email == get_jwt_identity()).one_or_none()
        if user and user.is_admin:
            args = flask_restful.request.get_json(force=True)
            msg = flask_mailman.EmailMessage(
                subject=args["subject"],
                body=args["body"],
                to=args["to"],
            )
            if args.get("is_html", False):
                msg.content_subtype = "html"
            status = bool(msg.send())
        else:
            status = False
        return {"status": status}


class StatusApi(flask_restful.Resource):
    def get(self):
        return {"message": "ok"}


class UserApi(flask_restful.Resource):
    @jwt_required()
    def get(self):
        return flask.jsonify(logged_in_as=get_jwt_identity())


api = flask_restful.Api(api_v1_bp)
api.add_resource(EmailApi, "/email")
api.add_resource(StatusApi, "/status")
api.add_resource(UserApi, "/user")
