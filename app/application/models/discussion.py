from __future__ import annotations
from datetime import (
    datetime,
    timezone,
)
from typing import (
    List,
    Union,
)

import sqlalchemy as sa
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.orm import (
    Mapped,
    mapped_column,
    relationship,
)

from application.models import (
    db,
    utcnow,
)
from application.util.exceptions import ModeratorRequired


__all__ = (
    "Ban",
    "Comment",
    "Discussion",
    "Thread",
    "Topic",
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


class Ban(db.Model):
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
    created_at = db.Column(
        db.DateTime(timezone=True),
        nullable=False,
        default=utcnow(),
    )
    created_by: Mapped["Discussion"] = relationship()
    discussion: Mapped["Discussion"] = relationship(
        back_populates="bans",
    )
    discussion_id: Mapped[int] = mapped_column(
        sa.ForeignKey("discussion.id"),
        nullable=False,
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


class Comment(db.Model):
    """Represents a single comment that could be a top level comment or a response to a parent comment"""

    id: Mapped[int] = mapped_column(
        nullable=False,
        primary_key=True,
    )
    body = sa.Column(
        sa.String,
        nullable=False,
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
    thread: Mapped["Thread"] = relationship(
        back_populates="comments",
    )
    thread_id: Mapped[int] = mapped_column(
        sa.ForeignKey("thread.id"),
        nullable=False,
    )

    def create_comment(self, *args, **kwargs) -> Comment:
        c = Comment(*args, discussion=self.discussion, parent=self, thread=self.thread, **kwargs)
        db.session.add(c)
        db.session.commit()
        return c


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
        back_populates="discussion",
        cascade="all, delete-orphan",
    )
    comments: Mapped[List["Comment"]] = relationship(
        back_populates="discussion",
        cascade="all, delete-orphan",
    )
    is_banned = sa.Column(
        sa.Boolean,
        default=False,
    )
    moderator_of: Mapped[List["Topic"]] = relationship(
        back_populates="moderators",
        secondary=topic_moderators,
    )
    subscriptions: Mapped[List["Topic"]] = relationship(
        back_populates="subscribers",
        secondary=subscription_subscriber,
    )
    threads: Mapped[List["Thread"]] = relationship(
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

    def create_thread(self, *args, **kwargs) -> Thread:
        t = Thread(*args, discussion=self, **kwargs)
        db.session.add(t)
        db.session.commit()
        return t

    def add_subscription(self, topic: Topic) -> None:
        self.subscriptions.append(topic)
        db.session.add(self)
        db.session.commit()


class Thread(db.Model):
    """Represents a discussion thread containing multiple comments"""

    id: Mapped[int] = mapped_column(
        nullable=False,
        primary_key=True,
    )
    topic: Mapped["Topic"] = relationship(
        back_populates="threads",
    )
    topic_id: Mapped[int] = mapped_column(
        sa.ForeignKey("topic.id"),
        nullable=False,
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
    title = sa.Column(
        sa.String,
        nullable=False,
    )

    def create_comment(self, *args, **kwargs) -> Comment:
        c = Comment(*args, discussion=self.discussion, thread=self, **kwargs)
        db.session.add(c)
        db.session.commit()
        return c


class Topic(db.Model):
    """Categories contain multiple threads that relate to a similar topic"""

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
    )
    is_deleted = sa.Column(
        sa.Boolean,
        default=False,
    )
    is_private = sa.Column(
        sa.Boolean,
        default=False,
    )
    moderators: Mapped[List["Discussion"]] = relationship(
        back_populates="moderator_of",
        secondary=topic_moderators,
    )
    name = sa.Column(
        sa.String,
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

    def create_ban(self, *args, created_by: Discussion, discussion: Discussion, **kwargs) -> Ban:
        if created_by in self.moderators:
            ban = Ban(*args, created_by=created_by, discussion=discussion, topic=self, **kwargs)
            db.session.add(ban)
            db.session.commit()
            return ban
        else:
            raise ModeratorRequired(f"{created_by.user} is not a moderator of {self.name}")
