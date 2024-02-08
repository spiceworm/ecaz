import http
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
from application.models import (
    AuthToken,
    User,
)
from application.util.misc import generate_unique_username


__all__ = ("api_misc_bp",)


api_misc_bp = flask.Blueprint(
    "api_misc_bp",
    __name__,
)


class GenerateUsernameApi(flask_restful.Resource):
    def get(self):
        return {"username": generate_unique_username()}


class StatusApi(flask_restful.Resource):
    def get(self):
        return {"message": "ok"}


class TerminalApi(flask_restful.Resource):
    @jwt_required()
    def post(self):
        user = User.from_jwt_identity(get_jwt_identity())
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


class VerifyEmailApi(flask_restful.Resource):
    @jwt_required()
    def post(self):
        if user := User.from_jwt_identity(get_jwt_identity()):
            if user.is_verified:
                return messages.ACCOUNT_ALREADY_VERIFIED, http.HTTPStatus.OK
            if User.query.filter_by(email=user.email, is_verified=True).one_or_none():
                return messages.EMAIL_VERIFIED_BY_DIFFERENT_ACCOUNT_ERROR, http.HTTPStatus.CONFLICT
            token = AuthToken.create_email_verification_token(user)
            url = flask.url_for("ui_bp.verify_email", jwt=token.value, _external=True)
            email = flask_mailman.EmailMessage(subject="Verify your account", body=url, to=[user.email])
            email.content_subtype = "html"
            email.send()
            return messages.VERIFICATION_EMAIL_SENT, http.HTTPStatus.OK
        return "", http.HTTPStatus.UNAUTHORIZED


api = flask_restful.Api(api_misc_bp)
api.add_resource(GenerateUsernameApi, "/generate-username")
api.add_resource(StatusApi, "/status")
api.add_resource(TerminalApi, "/terminal")
api.add_resource(VerifyEmailApi, "/verify-email")
