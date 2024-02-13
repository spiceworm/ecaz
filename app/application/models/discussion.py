from __future__ import annotations
from datetime import (
    datetime,
    timezone,
)
import functools
import secrets
from typing import (
    List,
    Union,
)

import humanize
import markdown
import slugify
import sqlalchemy as sa
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.orm import (
    Mapped,
    mapped_column,
    relationship,
)

from application.constants import expires
from application.models import (
    db,
    utcnow,
)
from application.util.exceptions import (
    ModeratorRequired,
    TopicSubscribeRequestError,
)


__all__ = (
    "Ban",
    "Comment",
    "Discussion",
    "Thread",
    "Topic",
    "TopicSubscribeRequest",
)


def default_thread_slug(ctx) -> str:
    """Make `Thread.slug` default to a slug of `Thread.title`"""
    title = ctx.get_current_parameters()["title"]
    return slugify.slugify(title)


# Association table for`discussion.saved_comments` <-> `comment.saves`
discussion_saved_comments = db.Table(
    "discussion_saved_comments",
    sa.Column(
        "comment_id",
        sa.ForeignKey("comment.id"),
        primary_key=True,
    ),
    sa.Column(
        "discussion_id",
        sa.ForeignKey("discussion.id"),
        primary_key=True,
    ),
)


# Association table for`discussion.subscriptions` <-> `topic.subscribers`
subscription_subscriber = db.Table(
    "subscription_subscriber",
    sa.Column(
        "topic_id",
        sa.ForeignKey("topic.id"),
        primary_key=True,
    ),
    sa.Column(
        "discussion_id",
        sa.ForeignKey("discussion.id"),
        primary_key=True,
    ),
)


# Association table for`discussion.saved_threads` <-> `thread.saves`
discussion_saved_threads = db.Table(
    "discussion_saved_threads",
    sa.Column(
        "threads_id",
        sa.ForeignKey("thread.id"),
        primary_key=True,
    ),
    sa.Column(
        "discussion_id",
        sa.ForeignKey("discussion.id"),
        primary_key=True,
    ),
)


# Association table for`discussion.moderator_of` <-> `topic.moderators`
topic_moderators = db.Table(
    "topic_moderators",
    sa.Column(
        "topic_id",
        sa.ForeignKey("topic.id"),
        primary_key=True,
    ),
    sa.Column(
        "discussion_id",
        sa.ForeignKey("discussion.id"),
        primary_key=True,
    ),
)


class BodyMixin:
    body = sa.Column(
        sa.String,
        nullable=False,
    )


class CreatedAtMixin:
    created_at = db.Column(
        db.DateTime(timezone=True),
        nullable=False,
        default=utcnow(),
    )

    @property
    def humanized_created_at(self) -> str:
        return humanize.naturaltime(self.created_at)


class IsHiddenMixin:
    is_hidden = sa.Column(
        sa.Boolean,
        default=False,
    )


class UniqueIdMixin:
    unique_id = sa.Column(
        sa.String,
        nullable=False,
        default=functools.partial(secrets.token_urlsafe, 16),
        index=True,
        unique=True,
    )


class VotingMixin:
    UPVOTE = 1
    DOWNVOTE = -1

    def _create_vote(self, discussion: Discussion, value: int) -> Union[CommentVote, None]:
        raise NotImplementedError  # pragma: no cover

    def downvote(self, discussion: Discussion) -> Union[CommentVote, ThreadVote]:
        self.delete_vote(discussion)
        return self._create_vote(discussion, self.DOWNVOTE)

    def upvote(self, discussion: Discussion) -> Union[CommentVote, ThreadVote]:
        self.delete_vote(discussion)
        return self._create_vote(discussion, self.UPVOTE)


class Ban(db.Model, CreatedAtMixin):
    """Object used to represent the action of banning a `User.discussion` from a `Topic`"""

    id: Mapped[int] = mapped_column(
        nullable=False,
        primary_key=True,
    )
    topic: Mapped["Topic"] = relationship(
        back_populates="bans",
    )
    topic_id: Mapped[int] = mapped_column(
        sa.ForeignKey("topic.id"),
        nullable=False,
    )
    created_by_id: Mapped[int] = mapped_column(
        sa.ForeignKey("discussion.id"),
        nullable=False,
    )
    created_by: Mapped["Discussion"] = relationship(
        foreign_keys=[created_by_id],
    )
    discussion_id: Mapped[int] = mapped_column(
        sa.ForeignKey("discussion.id"),
        nullable=False,
    )
    discussion: Mapped["Discussion"] = relationship(
        foreign_keys=[discussion_id],
    )
    expires_at = db.Column(
        db.DateTime(timezone=True),
    )
    is_shadow = sa.Column(
        sa.Boolean,
        default=False,
    )
    reason = db.Column(
        sa.String,
    )

    @property
    def humanized_expires_at(self) -> str:
        if not self.expires_at:
            return expires.NEVER
        return humanize.naturaltime(self.expires_at)

    @hybrid_property
    def is_active(self) -> Union[None, bool]:
        """Returns true if the ban is in effect and false otherwise"""
        return self.expires_at is None or self.expires_at >= datetime.now(tz=timezone.utc)

    @is_active.expression
    def is_active(self) -> sa.BooleanClauseList:
        """Returns true if the ban is in effect and false otherwise"""
        return sa.sql.or_(
            sa.sql.column("expires_at").is_(None),
            sa.sql.column("expires_at") >= datetime.now(tz=timezone.utc),
        )


class Comment(db.Model, BodyMixin, CreatedAtMixin, IsHiddenMixin, UniqueIdMixin, VotingMixin):
    """Represents a single comment that could be a top level comment or a response to a parent comment"""

    id: Mapped[int] = mapped_column(
        nullable=False,
        primary_key=True,
    )
    discussion: Mapped["Discussion"] = relationship(
        back_populates="comments",
    )
    discussion_id: Mapped[int] = mapped_column(
        sa.ForeignKey("discussion.id"),
        nullable=False,
    )
    is_deleted = sa.Column(
        sa.Boolean,
        default=False,
    )
    parent: Mapped["Comment"] = relationship(
        back_populates="responses",
        remote_side=[id],
    )
    parent_id: Mapped[int] = mapped_column(
        sa.ForeignKey("comment.id"),
        nullable=True,
    )
    responses: Mapped[List["Comment"]] = relationship(
        back_populates="parent",
        cascade="all, delete-orphan",
    )
    saves: Mapped[List["Discussion"]] = relationship(
        back_populates="saved_comments",
        secondary=discussion_saved_comments,
    )
    thread: Mapped["Thread"] = relationship(
        back_populates="comments",
    )
    thread_id: Mapped[int] = mapped_column(
        sa.ForeignKey("thread.id"),
        nullable=False,
    )
    votes: Mapped[List["CommentVote"]] = relationship(
        back_populates="comment",
        cascade="all, delete-orphan",
    )

    def create_comment(self, body: str, discussion: Discussion, **kwargs) -> Comment:
        c = Comment(body=body, discussion=discussion, parent=self, thread=self.thread, **kwargs)
        db.session.add(c)
        db.session.commit()
        return c

    def _create_vote(self, discussion: Discussion, value: int) -> Union[CommentVote, None]:
        # Do not allow multiple votes from the same user
        if not set(discussion.comment_votes).intersection(self.votes):
            vote = CommentVote(comment=self, discussion=discussion, value=value)
            db.session.add(vote)
            db.session.commit()
            return vote

    def delete_vote(self, discussion: Discussion) -> None:
        if votes := set(discussion.comment_votes).intersection(self.votes):
            vote = votes.pop()
            db.session.delete(vote)
            db.session.commit()

    def is_downvoted_by(self, discussion: Discussion) -> bool:
        if votes := set(discussion.comment_votes).intersection(self.votes):
            vote = votes.pop()
            return vote.value == self.DOWNVOTE
        return False

    def is_saved_by(self, discussion: Discussion) -> bool:
        return self in discussion.saved_comments

    def is_upvoted_by(self, discussion: Discussion) -> bool:
        if votes := set(discussion.comment_votes).intersection(self.votes):
            vote = votes.pop()
            return vote.value == self.UPVOTE
        return False

    def save(self, discussion: Discussion) -> None:
        if self not in discussion.saved_comments:
            discussion.saved_comments.append(self)
            db.session.add(self)
            db.session.commit()

    def unsave(self, discussion: Discussion) -> None:
        if self in discussion.saved_comments:
            discussion.saved_comments.remove(self)
            db.session.commit()


class CommentVote(db.Model):
    id: Mapped[int] = mapped_column(
        nullable=False,
        primary_key=True,
    )
    comment: Mapped["Comment"] = relationship(
        back_populates="votes",
    )
    comment_id: Mapped[int] = mapped_column(
        sa.ForeignKey("comment.id"),
        nullable=False,
    )
    discussion: Mapped["Discussion"] = relationship(
        back_populates="comment_votes",
    )
    discussion_id: Mapped[int] = mapped_column(
        sa.ForeignKey("discussion.id"),
        nullable=False,
    )
    value = sa.Column(
        sa.Integer,
    )  # 1 or -1


class Discussion(db.Model):
    """
    One-to-one relation that creates `User.discussion` namespace. Allows us to access:
        `User.discussion.comments`
        `User.discussion.threads`
        `Comment.discussion.user`
        `Thread.discussion.user`
    """

    id: Mapped[int] = mapped_column(
        nullable=False,
        primary_key=True,
    )
    bans: Mapped[List["Ban"]] = relationship(
        cascade="all, delete-orphan",
        foreign_keys=[Ban.discussion_id],
    )
    comments: Mapped[List["Comment"]] = relationship(
        back_populates="discussion",
        cascade="all, delete-orphan",
    )
    created_bans: Mapped[List["Ban"]] = relationship(
        cascade="all, delete-orphan",
        foreign_keys=[Ban.created_by_id],
    )
    is_banned = sa.Column(
        sa.Boolean,
        default=False,
    )
    moderator_of: Mapped[List["Topic"]] = relationship(
        back_populates="moderators",
        secondary=topic_moderators,
    )
    saved_comments: Mapped[List["Comment"]] = relationship(
        back_populates="saves",
        secondary=discussion_saved_comments,
    )
    saved_threads: Mapped[List["Thread"]] = relationship(
        back_populates="saves",
        secondary=discussion_saved_threads,
    )
    subscriptions: Mapped[List["Topic"]] = relationship(
        back_populates="subscribers",
        secondary=subscription_subscriber,
    )
    threads: Mapped[List["Thread"]] = relationship(
        back_populates="discussion",
        cascade="all, delete-orphan",
    )
    topic_subscribe_requests: Mapped[List["TopicSubscribeRequest"]] = relationship(
        back_populates="discussion",
        cascade="all, delete-orphan",
    )
    user: Mapped["User"] = relationship(
        back_populates="discussion",
    )
    user_id: Mapped[int] = mapped_column(
        sa.ForeignKey("user.id"),
        nullable=False,
    )
    comment_votes: Mapped[List["CommentVote"]] = relationship(
        back_populates="discussion",
        cascade="all, delete-orphan",
    )
    thread_votes: Mapped[List["ThreadVote"]] = relationship(
        back_populates="discussion",
        cascade="all, delete-orphan",
    )

    def add_subscription(self, topic: Topic) -> None:
        if not self.is_subscribed_to(topic):
            self.subscriptions.append(topic)
            db.session.add(self)
            db.session.commit()

    def create_subscribe_request(self, topic: Topic, **kwargs) -> Union[TopicSubscribeRequest, None]:
        if topic.is_private:
            if not self.has_subscribe_request_for(topic):
                subscribe_request = TopicSubscribeRequest(topic=topic, discussion=self, **kwargs)
                db.session.add(subscribe_request)
                db.session.commit()
                return subscribe_request
            return None
        else:
            raise TopicSubscribeRequestError("Subscribe requests are only used for private topics")

    def create_thread(self, body: str, title: str, topic: Topic, **kwargs) -> Thread:
        t = Thread(body=body, discussion=self, title=title, topic=topic, **kwargs)
        db.session.add(t)
        db.session.commit()
        return t

    def get_ban_for(self, topic: Topic) -> Union[Ban, None]:
        for ban in self.bans:
            if ban.topic == topic:
                return ban
        return

    def has_subscribe_request_for(self, topic: Topic) -> bool:
        for sr in self.topic_subscribe_requests:
            if sr.topic == topic:
                return True
        return False

    def is_banned_from(self, topic: Topic) -> bool:
        for ban in self.bans:
            if ban.topic == topic:
                return True
        return False

    def is_moderator_of(self, topic: Topic) -> bool:
        return self in topic.moderators

    def is_shadow_banned_from(self, topic: Topic) -> bool:
        for ban in self.bans:
            if ban.topic == topic:
                return ban.is_shadow
        return False

    def is_subscribed_to(self, topic: Topic) -> bool:
        return topic in self.subscriptions

    def remove_subscription(self, topic: Topic) -> None:
        if self.is_subscribed_to(topic):
            self.subscriptions.remove(topic)
            db.session.add(self)
            db.session.commit()


class Thread(db.Model, BodyMixin, CreatedAtMixin, IsHiddenMixin, UniqueIdMixin, VotingMixin):
    """Represents a discussion thread containing multiple comments"""

    id: Mapped[int] = mapped_column(
        nullable=False,
        primary_key=True,
    )
    comments: Mapped[List["Comment"]] = relationship(
        back_populates="thread",
        cascade="all, delete-orphan",
    )
    discussion: Mapped["Discussion"] = relationship(
        back_populates="threads",
    )
    discussion_id: Mapped[int] = mapped_column(
        sa.ForeignKey("discussion.id"),
        nullable=False,
    )
    is_deleted = sa.Column(
        sa.Boolean,
        default=False,
    )
    is_locked = sa.Column(
        sa.Boolean,
        default=False,
    )
    saves: Mapped[List["Discussion"]] = relationship(
        back_populates="saved_threads",
        secondary=discussion_saved_threads,
    )
    slug = sa.Column(
        sa.String,
        default=default_thread_slug,
        nullable=False,
    )
    topic: Mapped["Topic"] = relationship(
        back_populates="threads",
    )
    topic_id: Mapped[int] = mapped_column(
        sa.ForeignKey("topic.id"),
        nullable=False,
    )
    title = sa.Column(
        sa.String,
        nullable=False,
    )
    votes: Mapped[List["ThreadVote"]] = relationship(
        back_populates="thread",
        cascade="all, delete-orphan",
    )

    def create_comment(self, body: str, discussion: Discussion, **kwargs) -> Comment:
        c = Comment(body=body, discussion=discussion, thread=self, **kwargs)
        db.session.add(c)
        db.session.commit()
        return c

    def _create_vote(self, discussion: Discussion, value: int) -> Union[CommentVote, None]:
        # Do not allow multiple votes from the same user
        if not set(discussion.thread_votes).intersection(self.votes):
            vote = ThreadVote(thread=self, discussion=discussion, value=value)
            db.session.add(vote)
            db.session.commit()
            return vote

    def delete_vote(self, discussion: Discussion) -> None:
        if votes := set(discussion.thread_votes).intersection(self.votes):
            vote = votes.pop()
            db.session.delete(vote)
            db.session.commit()

    def is_downvoted_by(self, discussion: Discussion) -> bool:
        if votes := set(discussion.thread_votes).intersection(self.votes):
            vote = votes.pop()
            return vote.value == self.DOWNVOTE
        return False

    def is_saved_by(self, discussion: Discussion) -> bool:
        return self in discussion.saved_threads

    def is_upvoted_by(self, discussion: Discussion) -> bool:
        if votes := set(discussion.thread_votes).intersection(self.votes):
            vote = votes.pop()
            return vote.value == self.UPVOTE
        return False

    @property
    def markdown_body(self) -> str:
        return markdown.markdown(self.body)

    def save(self, discussion: Discussion) -> None:
        if self not in discussion.saved_threads:
            discussion.saved_threads.append(self)
            db.session.add(self)
            db.session.commit()

    def unsave(self, discussion: Discussion) -> None:
        if self in discussion.saved_threads:
            discussion.saved_threads.remove(self)
            db.session.commit()


class ThreadVote(db.Model):
    id: Mapped[int] = mapped_column(
        nullable=False,
        primary_key=True,
    )
    discussion: Mapped["Discussion"] = relationship(
        back_populates="thread_votes",
    )
    discussion_id: Mapped[int] = mapped_column(
        sa.ForeignKey("discussion.id"),
        nullable=False,
    )
    thread: Mapped["Thread"] = relationship(
        back_populates="votes",
    )
    thread_id: Mapped[int] = mapped_column(
        sa.ForeignKey("thread.id"),
        nullable=False,
    )
    value = sa.Column(
        sa.Integer,
    )  # 1 or -1


class Topic(db.Model, CreatedAtMixin):
    """Topics contain multiple threads that relate to a similar topic"""

    id: Mapped[int] = mapped_column(
        nullable=False,
        primary_key=True,
    )
    bans: Mapped[List["Ban"]] = relationship(
        back_populates="topic",
        cascade="all, delete-orphan",
    )
    description = sa.Column(
        sa.String,
        nullable=False,
    )
    is_deleted = sa.Column(
        sa.Boolean,
        default=False,
    )
    is_private = sa.Column(
        sa.Boolean,
        default=False,
    )
    subscribe_requests: Mapped[List["TopicSubscribeRequest"]] = relationship(
        back_populates="topic",
        cascade="all, delete-orphan",
    )
    moderators: Mapped[List["Discussion"]] = relationship(
        back_populates="moderator_of",
        secondary=topic_moderators,
    )
    name = sa.Column(
        sa.String,
        index=True,
        nullable=False,
        unique=True,
    )
    subscribers: Mapped[List["Discussion"]] = relationship(
        back_populates="subscriptions",
        secondary=subscription_subscriber,
    )
    threads: Mapped[List["Thread"]] = relationship(
        back_populates="topic",
        cascade="all, delete-orphan",
    )

    def add_moderator(self, discussion: Discussion) -> None:
        self.moderators.append(discussion)
        db.session.add(self)
        db.session.commit()

    def create_ban(self, created_by: Discussion, discussion: Discussion, **kwargs) -> Ban:
        if created_by.is_moderator_of(self):
            ban = Ban(created_by=created_by, discussion=discussion, topic=self, **kwargs)
            db.session.add(ban)
            db.session.commit()
            return ban
        else:
            raise ModeratorRequired(f"{created_by.user} is not a moderator of {self.name}")

    def create_thread(self, body: str, title: str, discussion: Discussion, **kwargs) -> Thread:
        thread = Thread(body=body, discussion=discussion, title=title, topic=self, **kwargs)
        db.session.add(thread)
        db.session.commit()
        return thread


class TopicSubscribeRequest(db.Model, CreatedAtMixin):
    id: Mapped[int] = mapped_column(
        nullable=False,
        primary_key=True,
    )
    topic: Mapped["Topic"] = relationship(
        back_populates="subscribe_requests",
    )
    topic_id: Mapped[int] = mapped_column(
        sa.ForeignKey("topic.id"),
        nullable=False,
    )
    discussion: Mapped["Discussion"] = relationship(
        back_populates="topic_subscribe_requests",
    )
    discussion_id: Mapped[int] = mapped_column(
        sa.ForeignKey("discussion.id"),
        nullable=False,
    )

    def approve(self, discussion: Discussion):
        if discussion.is_moderator_of(self.topic):
            self.discussion.add_subscription(self.topic)
            db.session.delete(self)
            db.session.commit()
        else:
            raise ModeratorRequired("Only moderators can approve a TopicSubscribeRequest")

    def deny(self, discussion: Discussion):
        if discussion.is_moderator_of(self.topic):
            db.session.delete(self)
            db.session.commit()
        else:
            raise ModeratorRequired("Only moderators can deny a TopicSubscribeRequest")
