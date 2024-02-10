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
    TopicSubscribeRequest,
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

    @jwt_required()
    def delete(self, unique_id):
        if user := User.from_jwt_identity(get_jwt_identity()):
            if obj := self.model.query.filter_by(discussion=user.discussion, unique_id=unique_id).one_or_none():
                obj.is_deleted = True
                db.session.add(obj)
                db.session.commit()
                return {}, http.HTTPStatus.OK
            return {}, http.HTTPStatus.NOT_FOUND
        return {}, http.HTTPStatus.UNAUTHORIZED

    def get(self, unique_id):
        if comment := self.model.query.filter_by(unique_id=unique_id).one_or_none():
            schema = self.schema()
            return schema.dump(comment), http.HTTPStatus.OK
        return {}, http.HTTPStatus.NOT_FOUND

    @jwt_required()
    def post(self, unique_id):
        if user := User.from_jwt_identity(get_jwt_identity()):
            parser = reqparse.RequestParser()
            parser.add_argument("body", required=True)
            args = parser.parse_args()
            if obj := self.model.query.filter_by(discussion=user.discussion, unique_id=unique_id).one_or_none():
                obj.body = args.body
                db.session.add(obj)
                db.session.commit()
                schema = self.schema()
                return schema.dump(obj), http.HTTPStatus.OK
            return {}, http.HTTPStatus.NOT_FOUND
        return {}, http.HTTPStatus.UNAUTHORIZED


class _CommentThreadSaveApiBase:
    model = None

    @jwt_required()
    def delete(self, unique_id):
        if user := User.from_jwt_identity(get_jwt_identity()):
            if obj := self.model.query.filter_by(unique_id=unique_id).one_or_none():
                obj.unsave(user.discussion)
                return {}, http.HTTPStatus.OK
            return {}, http.HTTPStatus.NOT_FOUND
        return {}, http.HTTPStatus.UNAUTHORIZED

    @jwt_required()
    def post(self, unique_id):
        if user := User.from_jwt_identity(get_jwt_identity()):
            if obj := self.model.query.filter_by(unique_id=unique_id).one_or_none():
                obj.save(user.discussion)
                return {}, http.HTTPStatus.OK
            return {}, http.HTTPStatus.NOT_FOUND
        return {}, http.HTTPStatus.UNAUTHORIZED


class _CommentThreadVoteApiBase:
    model = None

    @jwt_required()
    def post(self, unique_id):
        if user := User.from_jwt_identity(get_jwt_identity()):
            parser = reqparse.RequestParser()
            parser.add_argument("action", choices=("downvote", "upvote", "delete"), required=True)
            args = parser.parse_args()

            if obj := self.model.query.filter_by(unique_id=unique_id).one_or_none():
                match args.action:
                    case "downvote":
                        obj.downvote(discussion=user.discussion)
                    case "upvote":
                        obj.upvote(discussion=user.discussion)
                    case "delete":
                        obj.delete_vote(discussion=user.discussion)
                    case _:  # pragma: no cover
                        raise NotImplementedError(args.action)
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
        if _topic := Topic.query.filter_by(name=topic).one_or_none():
            schema = TopicSchema()
            return schema.dump(_topic), http.HTTPStatus.OK
        return {}, http.HTTPStatus.NOT_FOUND


class TopicSubscribeApi(flask_restful.Resource):
    @jwt_required()
    def delete(self, topic):
        if user := User.from_jwt_identity(get_jwt_identity()):
            if _topic := Topic.query.filter_by(name=topic).one_or_none():
                user.discussion.remove_subscription(_topic)
                return {}, http.HTTPStatus.OK
            return {}, http.HTTPStatus.NOT_FOUND
        return {}, http.HTTPStatus.UNAUTHORIZED

    @jwt_required()
    def post(self, topic):
        """
        Endpoint for users to subscribe to a topic that is not private. In order to subscribe to a private
        topic, a user needs to create a topic subscribe request which must be approved by a moderator of
        the private topic. However, if a user is already a moderator of a private topic, then they can use
        this endpoint to subscribe to that topic.
        """
        if user := User.from_jwt_identity(get_jwt_identity()):
            if _topic := Topic.query.filter_by(name=topic).one_or_none():
                if not _topic.is_private or user.discussion.is_moderator_of(_topic):
                    user.discussion.add_subscription(_topic)
                    return {}, http.HTTPStatus.OK
            return {}, http.HTTPStatus.NOT_FOUND
        return {}, http.HTTPStatus.UNAUTHORIZED


class TopicSubscribeRequestApi(flask_restful.Resource):
    @jwt_required()
    def delete(self, topic):
        """Endpoint for moderators to deny subscribe requests"""
        if user := User.from_jwt_identity(get_jwt_identity()):
            parser = reqparse.RequestParser()
            parser.add_argument("subscribe_request_id", required=True, type=int)
            args = parser.parse_args()
            if sr := TopicSubscribeRequest.query.filter_by(id=args.subscribe_request_id).one_or_none():
                if user.discussion.is_moderator_of(sr.topic):
                    sr.deny(user.discussion)
                    return {}, http.HTTPStatus.OK
                return {}, http.HTTPStatus.UNAUTHORIZED
        return {}, http.HTTPStatus.NOT_FOUND

    @jwt_required()
    def post(self, topic):
        """Endpoint for users to create subscribe requests for private topics"""
        if user := User.from_jwt_identity(get_jwt_identity()):
            if _topic := Topic.query.filter_by(name=topic, is_private=True).one_or_none():
                user.discussion.create_subscribe_request(_topic)
                return {}, http.HTTPStatus.OK
            return {}, http.HTTPStatus.NOT_FOUND
        return {}, http.HTTPStatus.UNAUTHORIZED

    @jwt_required()
    def put(self, topic):
        """Endpoint for moderators to approve subscribe requests"""
        if user := User.from_jwt_identity(get_jwt_identity()):
            parser = reqparse.RequestParser()
            parser.add_argument("subscribe_request_id", required=True, type=int)
            args = parser.parse_args()
            if sr := TopicSubscribeRequest.query.filter_by(id=args.subscribe_request_id).one_or_none():
                if user.discussion.is_moderator_of(sr.topic):
                    sr.approve(user.discussion)
                    return {}, http.HTTPStatus.OK
                return {}, http.HTTPStatus.UNAUTHORIZED
        return {}, http.HTTPStatus.NOT_FOUND


class CommentSaveApi(flask_restful.Resource, _CommentThreadSaveApiBase):
    model = Comment


class ThreadSaveApi(flask_restful.Resource, _CommentThreadSaveApiBase):
    model = Thread


class CommentVoteApi(flask_restful.Resource, _CommentThreadVoteApiBase):
    model = Comment


class ThreadVoteApi(flask_restful.Resource, _CommentThreadVoteApiBase):
    model = Thread


api = flask_restful.Api(api_discussion_bp)
api.add_resource(CommentApi, "/comment/<unique_id>")
api.add_resource(ThreadApi, "/thread/<unique_id>")
api.add_resource(CommentSaveApi, "/comment/<unique_id>/save")
api.add_resource(ThreadSaveApi, "/thread/<unique_id>/save")
api.add_resource(CommentVoteApi, "/comment/<unique_id>/vote")
api.add_resource(ThreadVoteApi, "/thread/<unique_id>/vote")
api.add_resource(TopicApi, "/topic/<topic>")
api.add_resource(TopicSubscribeApi, "/topic/<topic>/subscribe")
api.add_resource(TopicSubscribeRequestApi, "/topic/<topic>/subscribe/request")
