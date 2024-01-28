import shlex
import subprocess

import flask
import flask_mailman
import flask_restful
from flask_jwt_extended import (
    get_jwt_identity,
    jwt_required,
)

from application.constants import messages
from application.models import User
from application.util import generate_random_username


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


class GenerateUsernameApi(flask_restful.Resource):
    def get(self):
        username = generate_random_username()
        while User.query.filter_by(username=username).one_or_none():
            username = generate_random_username()
        return {"username": username}


class StatusApi(flask_restful.Resource):
    def get(self):
        return {"message": "ok"}


class TerminalApi(flask_restful.Resource):
    @jwt_required()
    def post(self):
        user = User.query.filter(User.email == get_jwt_identity()).one_or_none()
        if user and user.is_admin:
            data = flask_restful.request.get_json(force=True)
            command = data.get("command", "")
            command_parts = shlex.split(command)
            try:
                output = subprocess.check_output(command_parts).decode()
            except Exception as e:
                output = str(e)
        else:
            output = messages.RESTRICTED_TO_ADMIN
        return flask.jsonify(output=output.strip())


class UserApi(flask_restful.Resource):
    @jwt_required()
    def get(self):
        return flask.jsonify(logged_in_as=get_jwt_identity())


api = flask_restful.Api(api_v1_bp)
api.add_resource(EmailApi, "/email")
api.add_resource(GenerateUsernameApi, "/generate-username")
api.add_resource(StatusApi, "/status")
api.add_resource(TerminalApi, "/terminal")
api.add_resource(UserApi, "/user")
