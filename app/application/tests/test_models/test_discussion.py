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


def test_create_ban_as_non_mderator(user):
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
    t = d.create_thread(title="thread 1", topic=topic)
    c = t.create_comment(body="comment 1")
    r1 = c.create_comment(body="response 1")
    r2 = c.create_comment(body="response 2")
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
    t1 = d.create_thread(title="thread 1", topic=topic1)
    t2 = d.create_thread(title="thread 2", topic=topic2)
    assert t1.discussion is d
    assert t2.discussion is d
    assert t1.topic is topic1
    assert t2.topic is topic2


def test_relation_discussion_to_user(user):
    u = user()
    d = u.discussion
    assert d.user is u


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
    t = d.create_thread(title="thread 1", topic=topic)
    c1 = t.create_comment(body="comment 1")
    c2 = t.create_comment(body="comment 2")
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
