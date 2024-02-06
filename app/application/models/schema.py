from application.models import (
    Comment,
    Discussion,
    marshmallow,
    Thread,
    Topic,
    User,
)

__all__ = (
    "CommentSchema",
    "DiscussionSchema",
    "ThreadSchema",
    "TopicSchema",
    "UserSchema",
)


class UserSchema(marshmallow.SQLAlchemySchema):
    class Meta:
        model = User

    created_at = marshmallow.auto_field()
    username = marshmallow.auto_field()


class DiscussionSchema(marshmallow.SQLAlchemySchema):
    class Meta:
        model = Discussion

    user = marshmallow.Nested(UserSchema)


class TopicSchema(marshmallow.SQLAlchemySchema):
    class Meta:
        model = Topic

    created_at = marshmallow.auto_field()
    discussion = marshmallow.Nested(DiscussionSchema)
    name = marshmallow.auto_field()


class ThreadSchema(marshmallow.SQLAlchemySchema):
    class Meta:
        model = Thread

    body = marshmallow.auto_field()
    created_at = marshmallow.auto_field()
    discussion = marshmallow.Nested(DiscussionSchema)
    topic = marshmallow.Nested(TopicSchema)
    title = marshmallow.auto_field()
    unique_id = marshmallow.auto_field()


class CommentSchema(marshmallow.SQLAlchemySchema):
    class Meta:
        model = Comment

    body = marshmallow.auto_field()
    created_at = marshmallow.auto_field()
    discussion = marshmallow.Nested(DiscussionSchema)
    # If we are looking up a nested comment, there is no need to include the
    # `thread` attribute in the response for every other parent comment.
    # `thread` will already be included in the top level of the response json.
    parent = marshmallow.Nested(lambda: CommentSchema, exclude=("thread",))
    topic = marshmallow.Nested(TopicSchema)
    thread = marshmallow.Nested(ThreadSchema)
    unique_id = marshmallow.auto_field()
