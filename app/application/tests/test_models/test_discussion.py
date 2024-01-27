from datetime import (
    datetime,
    timedelta,
    timezone,
)

import pytest
import sqlalchemy as sa

from application.models import (
    Ban,
    db,
    Topic,
)
from application.util.exceptions import ModeratorRequired


@pytest.mark.parametrize(
    "expires_at, is_active",
    [
        (None, True),  # Never expires
        (datetime.now(tz=timezone.utc) + timedelta(days=1), True),  # Expires tomorrow
        (datetime.now(tz=timezone.utc) - timedelta(days=1), False),  # Expired yesterday
    ],
)
class TestBanIsActive:
    def test_hybrid_property(self, user, expires_at, is_active):
        d1 = user(email="1@test.com").discussion
        d2 = user(email="2@test.com").discussion
        topic = Topic(name="Topic", moderators=[d1])
        db.session.add(topic)
        db.session.commit()
        b = topic.create_ban(created_by=d1, discussion=d2, expires_at=expires_at)
        assert b.is_active is is_active

    def test_hybrid_property_expression(self, user, expires_at, is_active):
        d1 = user(email="1@test.com").discussion
        d2 = user(email="2@test.com").discussion
        topic = Topic(name="Topic", moderators=[d1])
        db.session.add(topic)
        db.session.commit()
        b = topic.create_ban(created_by=d1, discussion=d2, expires_at=expires_at)
        expected_bool = sa.true() if is_active else sa.false()
        assert Ban.query.filter(Ban.is_active == expected_bool).all() == [b]


def test_comment_is_downvoted_by(user):
    d = user().discussion
    topic = Topic(name="Topic 1")
    db.session.add(topic)
    db.session.commit()
    t = topic.create_thread(body="thread 1", title="title", discussion=d)
    c = t.create_comment(body="body", discussion=d)
    c.downvote(discussion=d)
    assert c.is_downvoted_by(d)


def test_comment_is_upvoted_by(user):
    d = user().discussion
    topic = Topic(name="Topic 1")
    db.session.add(topic)
    db.session.commit()
    t = topic.create_thread(body="thread 1", title="title", discussion=d)
    c = t.create_comment(body="body", discussion=d)
    c.upvote(discussion=d)
    assert c.is_upvoted_by(d)


def test_create_ban_as_non_moderator(user):
    d1 = user(email="1@test.com").discussion
    d2 = user(email="2@test.com").discussion
    topic = Topic(name="Test")
    db.session.add(topic)
    db.session.commit()
    with pytest.raises(ModeratorRequired):
        topic.create_ban(created_by=d1, discussion=d2)


def test_relation_comments_to_responses(user):
    u = user()
    d = u.discussion
    topic = Topic(name="Topic 1")
    db.session.add(topic)
    db.session.commit()
    t = d.create_thread(body="body", title="thread 1", topic=topic)
    c = t.create_comment(body="comment 1", discussion=d)
    r1 = c.create_comment(body="response 1", discussion=d)
    r2 = c.create_comment(body="response 2", discussion=d)
    assert r1.discussion is d
    assert r2.discussion is d
    assert r1.parent is c
    assert r2.parent is c
    assert t.comments == [c, r1, r2]
    assert t.topic is topic


def test_relation_discussion_to_threads(user):
    u = user()
    d = u.discussion
    topic1 = Topic(name="Topic 1")
    topic2 = Topic(name="Topic 2")
    db.session.add_all([topic1, topic2])
    db.session.commit()
    t1 = d.create_thread(body="body", title="thread 1", topic=topic1)
    t2 = d.create_thread(body="body", title="thread 2", topic=topic2)
    assert t1.discussion is d
    assert t2.discussion is d
    assert t1.topic is topic1
    assert t2.topic is topic2


def test_relation_discussion_to_user(user):
    u = user()
    d = u.discussion
    assert d.user is u


def test_relation_discussion_to_comment_votes(user):
    d1 = user(email="1@test.com").discussion
    d2 = user(email="2@test.com").discussion
    d3 = user(email="3@test.com").discussion
    topic = Topic(name="Topic 1")
    t1 = topic.create_thread(body="t1", discussion=d1, title="title 1")
    c1 = t1.create_comment(body="c1", discussion=d2)
    c2 = t1.create_comment(body="c2", discussion=d3)
    v1 = c1.upvote(discussion=d3)
    v2 = c2.upvote(discussion=d2)
    v3 = c1.upvote(discussion=d1)
    v4 = c2.upvote(discussion=d1)
    assert d1.comment_votes == [v3, v4]
    assert d2.comment_votes == [v2]
    assert d3.comment_votes == [v1]
    assert c1.votes == [v1, v3]
    assert c2.votes == [v2, v4]


def test_relation_discussion_to_thread_votes(user):
    d1 = user(email="1@test.com").discussion
    d2 = user(email="2@test.com").discussion
    d3 = user(email="3@test.com").discussion
    topic = Topic(name="Topic 1")
    t1 = topic.create_thread(body="t1", discussion=d1, title="title 1")
    t2 = topic.create_thread(body="t1", discussion=d1, title="title 1")
    v1 = t1.upvote(discussion=d2)
    v2 = t1.upvote(discussion=d3)
    v3 = t2.upvote(discussion=d2)
    assert d1.thread_votes == []
    assert d2.thread_votes == [v1, v3]
    assert d3.thread_votes == [v2]
    assert t1.votes == [v1, v2]
    assert t2.votes == [v3]


def test_relation_discussion_bans(user):
    d0 = user(email="0@test.com").discussion
    d1 = user(email="1@test.com").discussion
    d2 = user(email="2@test.com").discussion
    topic1 = Topic(name="Test Topic 1", moderators=[d0])
    topic2 = Topic(name="Test Topic 2", moderators=[d0])
    db.session.add_all([topic1, topic2])
    db.session.commit()
    b1 = topic1.create_ban(created_by=d0, discussion=d1)
    b2 = topic1.create_ban(created_by=d0, discussion=d2)
    b3 = topic2.create_ban(created_by=d0, discussion=d1)
    assert topic1.bans == [b1, b2]
    assert d1.bans == [b1, b3]
    assert b1.discussion is d1
    assert b3.discussion is d1


def test_relation_discussion_shadow_bans(user):
    d1 = user(email="1@test.com").discussion
    d2 = user(email="2@test.com").discussion
    topic1 = Topic(name="Test Topic 1", moderators=[d1])
    topic2 = Topic(name="Test Topic 2", moderators=[d1])
    b1 = topic1.create_ban(created_by=d1, discussion=d2, is_shadow=True)
    b2 = topic2.create_ban(created_by=d1, discussion=d2, is_shadow=True)
    assert d2.bans == [b1, b2]
    assert b1.discussion is d2
    assert b2.discussion is d2
    assert d2.bans[0].is_shadow
    assert d2.bans[1].is_shadow


def test_relation_multiple_comments_multiple_users(user):
    d1 = user(email="1@test.com").discussion
    d2 = user(email="2@test.com").discussion
    topic = Topic(name="Topic 1")
    db.session.add(topic)
    db.session.commit()
    t = d1.create_thread(body="body", title="thread 1", topic=topic)
    c1 = t.create_comment(body="comment 1", discussion=d1)
    c2 = t.create_comment(body="comment 2", discussion=d2)
    assert t.discussion is d1
    assert c1.discussion is d1
    assert c2.discussion is d2


def test_relation_subscription_subscriber(user):
    d1 = user(email="1@test.com").discussion
    d2 = user(email="2@test.com").discussion
    topic = Topic(name="Test Topic")
    db.session.add(topic)
    db.session.commit()
    d1.add_subscription(topic)
    d2.add_subscription(topic)
    assert d1.subscriptions == [topic]
    assert d2.subscriptions == [topic]
    assert topic.subscribers == [d1, d2]


def test_relation_threads_to_comments(user):
    u = user()
    d = u.discussion
    topic = Topic(name="Topic 1")
    db.session.add(topic)
    db.session.commit()
    t = d.create_thread(body="body", title="thread 1", topic=topic)
    c1 = t.create_comment(body="comment 1", discussion=d)
    c2 = t.create_comment(body="comment 2", discussion=d)
    assert c1.discussion is d
    assert c2.discussion is d
    assert c1.thread is t
    assert c2.thread is t
    assert t.comments == [c1, c2]
    assert t.topic is topic


def test_relation_topic_moderators(user):
    d1 = user(email="1@test.com").discussion
    d2 = user(email="2@test.com").discussion
    d3 = user(email="3@test.com").discussion
    topic1 = Topic(name="Test Topic 1", moderators=[d1, d2])
    topic2 = Topic(name="Test Topic 2", moderators=[d2, d3])
    db.session.add_all([topic1, topic2])
    db.session.commit()
    assert topic1.moderators == [d1, d2]
    assert topic2.moderators == [d2, d3]
    assert d1.moderator_of == [topic1]
    assert d2.moderator_of == [topic1, topic2]
    assert d3.moderator_of == [topic2]


def test_thread_is_downvoted_by(user):
    d = user().discussion
    topic = Topic(name="Topic 1")
    t = topic.create_thread(body="thread 1", title="title", discussion=d)
    t.downvote(discussion=d)
    assert t.is_downvoted_by(d)


def test_thread_is_upvoted_by(user):
    d = user().discussion
    topic = Topic(name="Topic 1")
    t = topic.create_thread(body="thread 1", title="title", discussion=d)
    t.upvote(discussion=d)
    assert t.is_upvoted_by(d)


def test_vote_on_comment(user):
    d = user().discussion
    topic = Topic(name="Topic 1")
    t = topic.create_thread(body="thread 1", title="title", discussion=d)
    c = t.create_comment(body="body", discussion=d)
    v1 = c.upvote(discussion=d)
    assert c.votes == [v1]
    v2 = c.downvote(discussion=d)
    assert c.votes == [v2]
    c.delete_vote(discussion=d)
    assert c.votes == []


def test_vote_on_thread(user):
    d = user().discussion
    topic = Topic(name="Topic 1")
    t = topic.create_thread(body="thread 1", title="title", discussion=d)
    v1 = t.upvote(discussion=d)
    assert t.votes == [v1]
    v2 = t.downvote(discussion=d)
    assert t.votes == [v2]
    t.delete_vote(discussion=d)
    assert t.votes == []
