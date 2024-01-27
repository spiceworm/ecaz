import flask
import flask_restful
from flask_restful import reqparse
from flask_jwt_extended import (
    get_jwt_identity,
    jwt_required,
)

from application.models import (
    Comment,
    Thread,
    User,
)


__all__ = ("api_discussion_bp",)


api_discussion_bp = flask.Blueprint(
    "api_discussion_bp",
    __name__,
    url_prefix="/discussion",
)


vote_parser = reqparse.RequestParser()
vote_parser.add_argument("unique_id", type=str, required=True)
vote_parser.add_argument("obj", choices=("comment", "thread"), required=True)
vote_parser.add_argument("action", choices=("downvote", "upvote", "delete"), required=True)


class VoteApi(flask_restful.Resource):
    @jwt_required()
    def post(self):
        if user := User.query.filter(User.email == get_jwt_identity()).one_or_none():
            args = vote_parser.parse_args()
            if args.obj == "comment":
                obj = Comment.query.filter_by(unique_id=args.unique_id).one_or_none()
            else:
                obj = Thread.query.filter_by(unique_id=args.unique_id).one_or_none()

            if obj:
                match args.action:
                    case "downvote":
                        obj.downvote(discussion=user.discussion)
                    case "upvote":
                        obj.upvote(discussion=user.discussion)
                    case "delete":
                        obj.delete_vote(discussion=user.discussion)
                    case _:
                        raise NotImplementedError(args.action)
                return {"success": "processed"}
            else:
                return {"error": "Invalid unique_id"}
        else:
            return {"error": "Invalid user"}


api = flask_restful.Api(api_discussion_bp)
api.add_resource(VoteApi, "/vote")
