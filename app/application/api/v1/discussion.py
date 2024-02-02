import http

import flask
from flask_jwt_extended import (
    get_jwt_identity,
    jwt_required,
)
import flask_restful
from flask_restful import reqparse

from application.models import (
    Comment,
    CommentSchema,
    db,
    Thread,
    ThreadSchema,
    Topic,
    TopicSchema,
    User,
)


__all__ = ("api_discussion_bp",)


api_discussion_bp = flask.Blueprint(
    "api_discussion_bp",
    __name__,
    url_prefix="/discussion",
)


class _CommentThreadApiBase:
    model = None
    schema = None

    def get(self, unique_id):
        if comment := self.model.query.filter_by(unique_id=unique_id).one_or_none():
            schema = self.schema()
            return schema.dump(comment)
        return {}, http.HTTPStatus.NOT_FOUND

    @jwt_required()
    def delete(self, unique_id):
        if user := User.query.filter(User.email == get_jwt_identity()).one_or_none():
            if obj := self.model.query.filter_by(discussion=user.discussion, unique_id=unique_id).one_or_none():
                obj.is_deleted = True
                db.session.add(obj)
                db.session.commit()
                return {}, http.HTTPStatus.OK
            return {}, http.HTTPStatus.NOT_FOUND
        return {}, http.HTTPStatus.UNAUTHORIZED


class CommentApi(flask_restful.Resource, _CommentThreadApiBase):
    model = Comment
    schema = CommentSchema


class ThreadApi(flask_restful.Resource, _CommentThreadApiBase):
    model = Thread
    schema = ThreadSchema


class TopicApi(flask_restful.Resource):
    def get(self, topic):
        if topic := Topic.query.filter_by(name=topic).one_or_none():
            schema = TopicSchema()
            return schema.dump(topic)
        return {}, http.HTTPStatus.NOT_FOUND


class _VoteApiBase:
    cls = None

    def post(self, unique_id):
        if user := User.query.filter(User.email == get_jwt_identity()).one_or_none():
            parser = reqparse.RequestParser()
            parser.add_argument("action", choices=("downvote", "upvote", "delete"), required=True)
            args = parser.parse_args()

            if obj := self.cls.query.filter_by(unique_id=unique_id).one_or_none():
                match args.action:
                    case "downvote":
                        obj.downvote(discussion=user.discussion)
                    case "upvote":
                        obj.upvote(discussion=user.discussion)
                    case "delete":
                        obj.delete_vote(discussion=user.discussion)
                    case _:  # pragma: no cover
                        raise NotImplementedError(args.action)
                return {"success": "processed"}
        return {}, http.HTTPStatus.NOT_FOUND


class CommentVoteApi(flask_restful.Resource, _VoteApiBase):
    cls = Comment

    @jwt_required()
    def post(self, unique_id):
        return super().post(unique_id)


class ThreadVoteApi(flask_restful.Resource, _VoteApiBase):
    cls = Thread

    @jwt_required()
    def post(self, unique_id):
        return super().post(unique_id)


api = flask_restful.Api(api_discussion_bp)
api.add_resource(CommentApi, "/comment/<unique_id>")
api.add_resource(CommentVoteApi, "/comment/<unique_id>/vote")
api.add_resource(ThreadApi, "/thread/<unique_id>")
api.add_resource(ThreadVoteApi, "/thread/<unique_id>/vote")
api.add_resource(TopicApi, "/topic/<topic>")
