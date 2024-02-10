from datetime import (
    datetime,
    timedelta,
    timezone,
)

import pytest
import sqlalchemy as sa

from application.models import Ban
from application.util.exceptions import (
    ModeratorRequired,
    TopicSubscribeRequestError,
)


class TestBan:
    def test_create_as_non_moderator(self, topic, user):
        d1 = user().discussion
        d2 = user().discussion
        _topic = topic()
        with pytest.raises(ModeratorRequired):
            _topic.create_ban(created_by=d1, discussion=d2)


@pytest.mark.parametrize(
    "expires_at, is_active",
    [
        (None, True),  # Never expires
        (datetime.now(tz=timezone.utc) + timedelta(days=1), True),  # Expires tomorrow
        (datetime.now(tz=timezone.utc) - timedelta(days=1), False),  # Expired yesterday
    ],
)
class TestBanIsActive:
    def test_hybrid_property(self, topic, user, expires_at, is_active):
        d1 = user().discussion
        d2 = user().discussion
        _topic = topic(moderators=[d1])
        b = _topic.create_ban(created_by=d1, discussion=d2, expires_at=expires_at)
        assert b.is_active is is_active

    def test_hybrid_property_expression(self, topic, user, expires_at, is_active):
        d1 = user().discussion
        d2 = user().discussion
        _topic = topic(moderators=[d1])
        b = _topic.create_ban(created_by=d1, discussion=d2, expires_at=expires_at)
        expected_bool = sa.true() if is_active else sa.false()
        assert Ban.query.filter(Ban.is_active == expected_bool).all() == [b]


class TestComment:
    def test_is_downvoted_by(self, comment, user):
        d1 = user().discussion
        d2 = user().discussion
        c = comment(body="body", discussion=d1)
        c.downvote(discussion=d1)
        assert c.is_downvoted_by(d1)
        assert not c.is_downvoted_by(d2)

    def test_is_upvoted_by(self, comment, user):
        d1 = user().discussion
        d2 = user().discussion
        c = comment(body="body", discussion=d1)
        c.upvote(discussion=d1)
        assert c.is_upvoted_by(d1)
        assert not c.is_upvoted_by(d2)

    def test_save(self, comment, user):
        d = user().discussion
        c = comment(discussion=d)
        c.save(d)
        assert d.saved_comments == [c]
        assert c.is_saved_by(d)
        c.unsave(d)
        assert d.saved_comments == []
        assert not c.is_saved_by(d)

    def test_vote(self, comment, user):
        d = user().discussion
        c = comment(discussion=d)
        v1 = c.upvote(discussion=d)
        assert c.votes == [v1]
        v2 = c.downvote(discussion=d)
        assert c.votes == [v2]
        c.delete_vote(discussion=d)
        assert c.votes == []


class TestDiscussion:
    def test_add_subscription(self, topic, user):
        u = user()
        t = topic()
        u.discussion.add_subscription(t)
        assert u.discussion.subscriptions == [t]

    def test_add_duplicate_subscription(self, topic, user):
        u = user()
        t = topic()
        u.discussion.add_subscription(t)
        u.discussion.add_subscription(t)
        u.discussion.add_subscription(t)
        assert u.discussion.subscriptions == [t]

    def test_is_subscribed_to(self, topic, user):
        u = user()
        t1 = topic(name="t1")
        t2 = topic(name="t2")
        u.discussion.add_subscription(t1)
        assert u.discussion.subscriptions == [t1]
        assert u.discussion.is_subscribed_to(t1)
        assert not u.discussion.is_subscribed_to(t2)

    def test_remove_subscription(self, topic, user):
        u = user()
        t = topic()
        u.discussion.add_subscription(t)
        assert u.discussion.subscriptions == [t]
        u.discussion.remove_subscription(t)
        assert u.discussion.subscriptions == []

    def test_remove_nonexistent_subscription(self, topic, user):
        u = user()
        t = topic()
        u.discussion.remove_subscription(t)
        assert u.discussion.subscriptions == []


class TestThread:
    def test_is_downvoted_by(self, thread, user):
        d1 = user().discussion
        d2 = user().discussion
        t = thread(discussion=d1)
        t.downvote(discussion=d1)
        assert t.is_downvoted_by(d1)
        assert not t.is_downvoted_by(d2)

    def test_is_upvoted_by(self, thread, user):
        d1 = user().discussion
        d2 = user().discussion
        t = thread(discussion=d1)
        t.upvote(discussion=d1)
        assert t.is_upvoted_by(d1)
        assert not t.is_upvoted_by(d2)

    def test_save(self, thread, user):
        d = user().discussion
        t = thread(discussion=d)
        t.save(d)
        assert d.saved_threads == [t]
        assert t.is_saved_by(d)
        t.unsave(d)
        assert d.saved_threads == []
        assert not t.is_saved_by(d)

    def test_vote(self, thread, user):
        d = user().discussion
        t = thread(discussion=d)
        v1 = t.upvote(discussion=d)
        assert t.votes == [v1]
        v2 = t.downvote(discussion=d)
        assert t.votes == [v2]
        t.delete_vote(discussion=d)
        assert t.votes == []


class TestTopic:
    def test_add_moderator(self, topic, user):
        t = topic()
        d1 = user().discussion
        d2 = user().discussion
        t.add_moderator(d1)
        assert d1.is_moderator_of(t)
        assert not d2.is_moderator_of(t)


class TestTopicSubscribeRequest:
    def test_approve(self, topic, user):
        d1 = user().discussion
        d2 = user().discussion
        t = topic(is_private=True)
        t.add_moderator(d2)
        sr = d1.create_subscribe_request(t)
        assert not d1.is_subscribed_to(t)
        sr.approve(d2)
        assert d1.is_subscribed_to(t)

    def test_approve_as_not_moderator(self, topic, user):
        d1 = user().discussion
        d2 = user().discussion
        t = topic(is_private=True)
        sr = d1.create_subscribe_request(t)
        with pytest.raises(ModeratorRequired):
            sr.approve(d2)

    def test_create_for_not_private_topic(self, topic, user):
        d = user().discussion
        t = topic(is_private=False)
        with pytest.raises(TopicSubscribeRequestError):
            d.create_subscribe_request(t)

    def test_deny(self, topic, user):
        d1 = user().discussion
        d2 = user().discussion
        t = topic(is_private=True)
        t.add_moderator(d2)
        sr = d1.create_subscribe_request(t)
        assert not d1.is_subscribed_to(t)
        sr.deny(d2)
        assert not d1.is_subscribed_to(t)

    def test_deny_as_not_moderator(self, topic, user):
        d1 = user().discussion
        d2 = user().discussion
        t = topic(is_private=True)
        sr = d1.create_subscribe_request(t)
        with pytest.raises(ModeratorRequired):
            sr.deny(d2)

    def test_has_subscribe_request_for(self, topic, user):
        d = user().discussion
        t1 = topic(name="t1", is_private=True)
        t2 = topic(name="t2", is_private=True)
        d.create_subscribe_request(t1)
        assert d.has_subscribe_request_for(t1)
        assert not d.has_subscribe_request_for(t2)


class TestRelation:
    def test_comments_to_responses(self, topic, user):
        u = user()
        d = u.discussion
        _topic = topic()
        t = d.create_thread(body="body", title="thread 1", topic=_topic)
        c = t.create_comment(body="comment 1", discussion=d)
        r1 = c.create_comment(body="response 1", discussion=d)
        r2 = c.create_comment(body="response 2", discussion=d)
        assert r1.discussion is d
        assert r2.discussion is d
        assert r1.parent is c
        assert r2.parent is c
        assert t.comments == [c, r1, r2]
        assert t.topic is _topic

    def test_discussion_to_bans(self, topic, user):
        d0 = user(email="0@test.com").discussion
        d1 = user().discussion
        d2 = user().discussion
        topic1 = topic(name="t1", moderators=[d0])
        topic2 = topic(name="t2", moderators=[d0])
        b1 = topic1.create_ban(created_by=d0, discussion=d1)
        b2 = topic1.create_ban(created_by=d0, discussion=d2)
        b3 = topic2.create_ban(created_by=d0, discussion=d1)
        assert topic1.bans == [b1, b2]
        assert d1.bans == [b1, b3]
        assert b1.discussion is d1
        assert b3.discussion is d1

    def test_discussion_to_comment_votes(self, topic, user):
        d1 = user().discussion
        d2 = user().discussion
        d3 = user(email="3@test.com").discussion
        _topic = topic()
        t1 = _topic.create_thread(body="t1", discussion=d1, title="title 1")
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

    def test_discussion_to_subscribe_request(self, topic, user):
        d = user().discussion
        t = topic(is_private=True)
        sr = d.create_subscribe_request(t)
        assert d.topic_subscribe_requests == [sr]
        assert t.subscribe_requests == [sr]
        assert sr.topic == t
        assert sr.discussion == d

    def test_discussion_to_thread_votes(self, topic, user):
        d1 = user().discussion
        d2 = user().discussion
        d3 = user(email="3@test.com").discussion
        _topic = topic()
        t1 = _topic.create_thread(body="t1", discussion=d1, title="title 1")
        t2 = _topic.create_thread(body="t1", discussion=d1, title="title 1")
        v1 = t1.upvote(discussion=d2)
        v2 = t1.upvote(discussion=d3)
        v3 = t2.upvote(discussion=d2)
        assert d1.thread_votes == []
        assert d2.thread_votes == [v1, v3]
        assert d3.thread_votes == [v2]
        assert t1.votes == [v1, v2]
        assert t2.votes == [v3]

    def test_discussion_to_threads(self, topic, user):
        u = user()
        d = u.discussion
        topic1 = topic(name="t1")
        topic2 = topic(name="t2")
        t1 = d.create_thread(body="body", title="thread 1", topic=topic1)
        t2 = d.create_thread(body="body", title="thread 2", topic=topic2)
        assert t1.discussion is d
        assert t2.discussion is d
        assert t1.topic is topic1
        assert t2.topic is topic2

    def test_discussion_to_user(self, user):
        u = user()
        d = u.discussion
        assert d.user is u

    def test_discussion_to_shadow_bans(self, topic, user):
        d1 = user().discussion
        d2 = user().discussion
        topic1 = topic(name="t1", moderators=[d1])
        topic2 = topic(name="t2", moderators=[d1])
        b1 = topic1.create_ban(created_by=d1, discussion=d2, is_shadow=True)
        b2 = topic2.create_ban(created_by=d1, discussion=d2, is_shadow=True)
        assert d2.bans == [b1, b2]
        assert b1.discussion is d2
        assert b2.discussion is d2
        assert d2.bans[0].is_shadow
        assert d2.bans[1].is_shadow

    def test_multiple_comments_to_multiple_users(self, thread, user):
        d1 = user().discussion
        d2 = user().discussion
        t = thread(discussion=d1)
        c1 = t.create_comment(body="comment 1", discussion=d1)
        c2 = t.create_comment(body="comment 2", discussion=d2)
        assert t.discussion is d1
        assert c1.discussion is d1
        assert c2.discussion is d2

    def test_subscription_to_subscriber(self, topic, user):
        d1 = user().discussion
        d2 = user().discussion
        _topic = topic()
        d1.add_subscription(_topic)
        d2.add_subscription(_topic)
        assert d1.subscriptions == [_topic]
        assert d2.subscriptions == [_topic]
        assert _topic.subscribers == [d1, d2]

    def test_threads_to_comments(self, topic, user):
        u = user()
        d = u.discussion
        _topic = topic()
        t = d.create_thread(body="body", title="thread 1", topic=_topic)
        c1 = t.create_comment(body="comment 1", discussion=d)
        c2 = t.create_comment(body="comment 2", discussion=d)
        assert c1.discussion is d
        assert c2.discussion is d
        assert c1.thread is t
        assert c2.thread is t
        assert t.comments == [c1, c2]
        assert t.topic is _topic

    def test_topic_moderators(self, topic, user):
        d1 = user().discussion
        d2 = user().discussion
        d3 = user(email="3@test.com").discussion
        topic1 = topic(name="t1", moderators=[d1, d2])
        topic2 = topic(name="t2", moderators=[d2, d3])
        assert topic1.moderators == [d1, d2]
        assert topic2.moderators == [d2, d3]
        assert d1.moderator_of == [topic1]
        assert d2.moderator_of == [topic1, topic2]
        assert d3.moderator_of == [topic2]
