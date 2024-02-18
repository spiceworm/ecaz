import http

from flask import url_for
import pytest


class TestCommentApi:
    endpoint = "api_discussion_bp.commentapi"

    def test_delete(self, api_user, comment):
        user = api_user()
        c = comment(discussion=user.discussion)
        resp = user.delete(url_for(self.endpoint, unique_id=c.unique_id))
        assert resp.status_code == http.HTTPStatus.OK
        assert c.is_deleted

    def test_delete_if_created_by_different_user(self, api_user, comment, user):
        user1 = api_user()
        user2 = user()
        c = comment(discussion=user2.discussion)
        resp = user1.delete(url_for(self.endpoint, unique_id=c.unique_id))
        assert resp.status_code == http.HTTPStatus.NOT_FOUND
        assert not c.is_deleted

    def test_delete_using_bad_auth_token(self, bad_auth_token_api_user, comment):
        user = bad_auth_token_api_user()
        c = comment(discussion=user.discussion)
        resp = user.delete(url_for(self.endpoint, unique_id=c.unique_id))
        assert resp.status_code == http.HTTPStatus.UNAUTHORIZED
        assert not c.is_deleted

    def test_edit(self, api_user, comment):
        u = api_user()
        c = comment(discussion=u.discussion)
        updated_body = "This is the updated comment body string"
        assert c.body != updated_body
        resp = u.post(url_for(self.endpoint, unique_id=c.unique_id), json={"body": updated_body})
        assert resp.json["body"] == updated_body
        assert c.body == updated_body
        assert resp.status_code == http.HTTPStatus.OK

    def test_edit_if_created_by_different_user(self, api_user, comment):
        u1 = api_user()
        u2 = api_user()
        c = comment(discussion=u1.discussion)
        updated_body = "This is the updated comment body string but no update should occur"
        assert c.body != updated_body
        resp = u2.post(url_for(self.endpoint, unique_id=c.unique_id), json={"body": updated_body})
        assert resp.json == {}
        assert c.body != updated_body
        assert resp.status_code == http.HTTPStatus.NOT_FOUND

    def test_edit_using_bad_auth_token(self, bad_auth_token_api_user, comment):
        u = bad_auth_token_api_user()
        c = comment(discussion=u.discussion)
        updated_body = "This is the updated comment body string"
        assert c.body != updated_body
        resp = u.post(url_for(self.endpoint, unique_id=c.unique_id), json={"body": updated_body})
        assert resp.status_code == http.HTTPStatus.UNAUTHORIZED
        assert c.body != updated_body

    def test_get_nested_comment(self, comment, client, user):
        u = user()
        parent_comment = comment(discussion=u.discussion)
        nested_comment = parent_comment.create_comment(body="b", discussion=u.discussion)
        resp = client.get(url_for(self.endpoint, unique_id=nested_comment.unique_id))
        assert resp.json == {
            "body": nested_comment.body,
            "created_at": nested_comment.created_at.isoformat(),
            "discussion": {
                "user": {
                    "created_at": nested_comment.discussion.user.created_at.isoformat(),
                    "username": nested_comment.discussion.user.username,
                }
            },
            "parent": {
                "body": parent_comment.body,
                "created_at": parent_comment.created_at.isoformat(),
                "discussion": {
                    "user": {
                        "created_at": parent_comment.discussion.user.created_at.isoformat(),
                        "username": parent_comment.discussion.user.username,
                    }
                },
                "parent": None,
                "unique_id": parent_comment.unique_id,
            },
            "thread": {
                "body": nested_comment.thread.body,
                "created_at": nested_comment.thread.created_at.isoformat(),
                "discussion": {
                    "user": {
                        "created_at": nested_comment.thread.discussion.user.created_at.isoformat(),
                        "username": nested_comment.thread.discussion.user.username,
                    }
                },
                "topic": {
                    "created_at": nested_comment.thread.topic.created_at.isoformat(),
                    "name": nested_comment.thread.topic.name,
                },
                "title": nested_comment.thread.title,
                "unique_id": nested_comment.thread.unique_id,
            },
            "unique_id": nested_comment.unique_id,
        }

    def test_get_top_level_comment(self, comment, client, user):
        u = user()
        c = comment(discussion=u.discussion)
        resp = client.get(url_for(self.endpoint, unique_id=c.unique_id))
        assert resp.json == {
            "body": c.body,
            "created_at": c.created_at.isoformat(),
            "discussion": {
                "user": {"created_at": c.discussion.user.created_at.isoformat(), "username": c.discussion.user.username}
            },
            "parent": None,
            "thread": {
                "body": c.thread.body,
                "created_at": c.thread.created_at.isoformat(),
                "discussion": {
                    "user": {
                        "created_at": c.thread.discussion.user.created_at.isoformat(),
                        "username": c.thread.discussion.user.username,
                    }
                },
                "topic": {
                    "created_at": c.thread.topic.created_at.isoformat(),
                    "name": c.thread.topic.name,
                },
                "title": c.thread.title,
                "unique_id": c.thread.unique_id,
            },
            "unique_id": c.unique_id,
        }

    def test_get_using_invalid_unique_id(self, client):
        resp = client.get(url_for(self.endpoint, unique_id="this-is-invalid"))
        assert resp.status_code == http.HTTPStatus.NOT_FOUND


class TestThread:
    endpoint = "api_discussion_bp.threadapi"

    def test_delete(self, api_user, thread):
        user = api_user()
        t = thread(discussion=user.discussion)
        resp = user.delete(url_for(self.endpoint, unique_id=t.unique_id))
        assert resp.status_code == http.HTTPStatus.OK
        assert t.is_deleted

    def test_delete_if_created_by_different_user(self, api_user, thread):
        user1 = api_user()
        user2 = api_user(email="2@tets.com")
        t = thread(discussion=user2.discussion)
        resp = user1.delete(url_for(self.endpoint, unique_id=t.unique_id))
        assert resp.status_code == http.HTTPStatus.NOT_FOUND
        assert not t.is_deleted

    def test_delete_using_bad_auth_token(self, bad_auth_token_api_user, thread):
        user = bad_auth_token_api_user()
        t = thread(discussion=user.discussion)
        resp = user.delete(url_for(self.endpoint, unique_id=t.unique_id))
        assert resp.status_code == http.HTTPStatus.UNAUTHORIZED
        assert not t.is_deleted

    def test_edit(self, api_user, thread):
        u = api_user()
        t = thread(discussion=u.discussion)
        updated_body = "This is the updated thread body string"
        assert t.body != updated_body
        resp = u.post(url_for(self.endpoint, unique_id=t.unique_id), json={"body": updated_body})
        assert resp.json["body"] == updated_body
        assert t.body == updated_body
        assert resp.status_code == http.HTTPStatus.OK

    def test_edit_if_created_by_different_user(self, api_user, thread):
        u1 = api_user()
        u2 = api_user()
        t = thread(discussion=u1.discussion)
        updated_body = "This is the updated thread body string but no update should occur"
        assert t.body != updated_body
        resp = u2.post(url_for(self.endpoint, unique_id=t.unique_id), json={"body": updated_body})
        assert resp.json == {}
        assert t.body != updated_body
        assert resp.status_code == http.HTTPStatus.NOT_FOUND

    def test_edit_using_bad_auth_token(self, bad_auth_token_api_user, thread):
        u = bad_auth_token_api_user()
        t = thread(discussion=u.discussion)
        updated_body = "This is the updated thread body string"
        assert t.body != updated_body
        resp = u.post(url_for(self.endpoint, unique_id=t.unique_id), json={"body": updated_body})
        assert resp.status_code == http.HTTPStatus.UNAUTHORIZED
        assert t.body != updated_body

    def test_get(self, client, thread, user):
        u = user()
        t = thread(discussion=u.discussion)
        resp = client.get(url_for(self.endpoint, unique_id=t.unique_id))
        assert resp.json == {
            "body": t.body,
            "created_at": t.created_at.isoformat(),
            "discussion": {
                "user": {"created_at": t.discussion.user.created_at.isoformat(), "username": t.discussion.user.username}
            },
            "topic": {"created_at": t.topic.created_at.isoformat(), "name": t.topic.name},
            "title": t.title,
            "unique_id": t.unique_id,
        }

    def test_get_using_invalid_unique_id(self, client):
        resp = client.get(url_for(self.endpoint, unique_id="this-is-invalid"))
        assert resp.status_code == http.HTTPStatus.NOT_FOUND


class TestSaveCommentApi:
    endpoint = "api_discussion_bp.commentsaveapi"

    def test_save(self, api_user, comment):
        user = api_user()
        c = comment(discussion=user.discussion)
        url = url_for(self.endpoint, unique_id=c.unique_id)

        resp1 = user.post(url)
        assert resp1.status_code == http.HTTPStatus.OK
        assert user.discussion.saved_comments == [c]

    def test_save_as_nonexistent_user(self, bad_auth_token_api_user, comment):
        user = bad_auth_token_api_user()
        c = comment(discussion=user.discussion)
        url = url_for(self.endpoint, unique_id=c.unique_id)
        resp1 = user.post(url)
        assert resp1.status_code == http.HTTPStatus.UNAUTHORIZED

    def test_save_delete(self, api_user, comment):
        user = api_user()
        c = comment(discussion=user.discussion)
        url = url_for(self.endpoint, unique_id=c.unique_id)

        resp1 = user.post(url)
        assert resp1.status_code == http.HTTPStatus.OK
        assert user.discussion.saved_comments == [c]

        resp2 = user.delete(url)
        assert resp2.status_code == http.HTTPStatus.OK
        assert user.discussion.saved_comments == []

    def test_save_delete_as_nonexistent_user(self, bad_auth_token_api_user, comment):
        user = bad_auth_token_api_user()
        c = comment(discussion=user.discussion)
        url = url_for(self.endpoint, unique_id=c.unique_id)
        resp1 = user.delete(url)
        assert resp1.status_code == http.HTTPStatus.UNAUTHORIZED

    def test_save_delete_using_invalid_unique_id(self, api_user):
        user = api_user()
        url = url_for(self.endpoint, unique_id="this-is-invalid")
        resp1 = user.delete(url)
        assert resp1.status_code == http.HTTPStatus.NOT_FOUND

    def test_save_using_invalid_unique_id(self, api_user):
        user = api_user()
        url = url_for(self.endpoint, unique_id="this-is-invalid")
        resp1 = user.post(url)
        assert resp1.status_code == http.HTTPStatus.NOT_FOUND


class TestSaveThreadApi:
    endpoint = "api_discussion_bp.threadsaveapi"

    def test_save(self, api_user, thread):
        user = api_user()
        t = thread(discussion=user.discussion)
        url = url_for(self.endpoint, unique_id=t.unique_id)

        resp1 = user.post(url)
        assert resp1.status_code == http.HTTPStatus.OK
        assert user.discussion.saved_threads == [t]

        resp2 = user.delete(url)
        assert resp2.status_code == http.HTTPStatus.OK
        assert user.discussion.saved_threads == []

    def test_save_as_nonexistent_user(self, bad_auth_token_api_user, thread):
        user = bad_auth_token_api_user()
        t = thread(discussion=user.discussion)
        url = url_for(self.endpoint, unique_id=t.unique_id)
        resp1 = user.post(url)
        assert resp1.status_code == http.HTTPStatus.UNAUTHORIZED

    def test_save_delete(self, api_user, thread):
        user = api_user()
        t = thread(discussion=user.discussion)
        url = url_for(self.endpoint, unique_id=t.unique_id)

        resp1 = user.post(url)
        assert user.discussion.saved_threads == [t]
        assert resp1.status_code == http.HTTPStatus.OK

        resp2 = user.delete(url)
        assert resp2.status_code == http.HTTPStatus.OK
        assert user.discussion.saved_threads == []

    def test_save_delete_as_nonexistent_user(self, bad_auth_token_api_user, thread):
        user = bad_auth_token_api_user()
        t = thread(discussion=user.discussion)
        url = url_for(self.endpoint, unique_id=t.unique_id)
        resp1 = user.delete(url)
        assert resp1.status_code == http.HTTPStatus.UNAUTHORIZED

    def test_save_delete_using_invalid_unique_id(self, api_user):
        user = api_user()
        url = url_for(self.endpoint, unique_id="this-is-invalid")
        resp1 = user.delete(url)
        assert resp1.status_code == http.HTTPStatus.NOT_FOUND

    def test_save_using_invalid_unique_id(self, api_user):
        user = api_user()
        url = url_for(self.endpoint, unique_id="this-is-invalid")
        resp1 = user.post(url)
        assert resp1.status_code == http.HTTPStatus.NOT_FOUND


class TestTopicApi:
    endpoint = "api_discussion_bp.topicapi"

    def test_get(self, client, topic):
        _topic = topic()
        resp = client.get(url_for(self.endpoint, topic=_topic.name))
        assert resp.json == {"created_at": _topic.created_at.isoformat(), "name": _topic.name}

    def test_get_using_invalid_name(self, client):
        resp = client.get(url_for(self.endpoint, topic="this-is-invalid"))
        assert resp.status_code == http.HTTPStatus.NOT_FOUND


class TestTopicBanApi:
    endpoint = "api_discussion_bp.topicbanapi"

    def test_delete(self, api_user, topic):
        u1 = api_user()
        u2 = api_user()
        t = topic(moderators=[u1.discussion])
        ban = t.create_ban(created_by=u1.discussion, discussion=u2.discussion)
        assert u2.discussion.topic_bans == [ban]
        resp = u1.delete(url_for(self.endpoint, topic=t.name), json={"topic_ban_id": ban.id})
        assert resp.status_code == http.HTTPStatus.OK
        assert u2.discussion.topic_bans == []

    def test_delete_if_invalid_topic(self, api_user, topic):
        u1 = api_user()
        u2 = api_user()
        t = topic(moderators=[u1.discussion])
        ban = t.create_ban(created_by=u1.discussion, discussion=u2.discussion)
        assert u2.discussion.topic_bans == [ban]
        resp = u1.delete(url_for(self.endpoint, topic="this-is-invalid"), json={"topic_ban_id": ban.id + 1})
        assert resp.status_code == http.HTTPStatus.NOT_FOUND
        assert u2.discussion.topic_bans == [ban]

    def test_delete_if_invalid_topic_ban_id(self, api_user, topic):
        u1 = api_user()
        u2 = api_user()
        t = topic(moderators=[u1.discussion])
        ban = t.create_ban(created_by=u1.discussion, discussion=u2.discussion)
        assert u2.discussion.topic_bans == [ban]
        resp = u1.delete(url_for(self.endpoint, topic=t.name), json={"topic_ban_id": ban.id + 1})
        assert resp.status_code == http.HTTPStatus.NOT_FOUND
        assert u2.discussion.topic_bans == [ban]

    def test_delete_if_invalid_user(self, bad_auth_token_api_user, api_user, topic):
        u0 = bad_auth_token_api_user()
        u1 = api_user()
        u2 = api_user()
        t = topic(moderators=[u1.discussion])
        ban = t.create_ban(created_by=u1.discussion, discussion=u2.discussion)
        assert u2.discussion.topic_bans == [ban]
        resp = u0.delete(url_for(self.endpoint, topic=t.name), json={"topic_ban_id": ban.id})
        assert resp.status_code == http.HTTPStatus.NOT_FOUND
        assert u2.discussion.topic_bans == [ban]

    def test_delete_if_not_moderator(self, api_user, topic):
        u1 = api_user()
        u2 = api_user()
        t = topic(moderators=[u1.discussion])
        ban = t.create_ban(created_by=u1.discussion, discussion=u2.discussion)
        assert u2.discussion.topic_bans == [ban]
        resp = u2.delete(url_for(self.endpoint, topic=t.name), json={"topic_ban_id": ban.id})
        assert resp.status_code == http.HTTPStatus.UNAUTHORIZED
        assert u2.discussion.topic_bans == [ban]


class TestTopicSubscribeApi:
    endpoint = "api_discussion_bp.topicsubscribeapi"

    def test_add(self, api_user, topic):
        user = api_user()
        t = topic()
        resp = user.post(url_for(self.endpoint, topic=t.name))
        assert resp.json == {}
        assert resp.status_code == http.HTTPStatus.OK
        assert user.discussion.subscriptions == [t]

    def test_add_as_nonexistent_user(self, bad_auth_token_api_user, topic):
        user = bad_auth_token_api_user()
        t = topic()
        resp = user.post(url_for(self.endpoint, topic=t.name))
        assert resp.status_code == http.HTTPStatus.UNAUTHORIZED

    def test_add_if_is_private_topic(self, api_user, topic):
        user = api_user()
        t = topic(is_private=True)
        resp = user.post(url_for(self.endpoint, topic=t.name))
        assert not user.discussion.is_subscribed_to(t)
        assert resp.status_code == http.HTTPStatus.NOT_FOUND

    def test_add_if_is_private_topic_and_user_is_moderator_of_topic(self, api_user, topic):
        user = api_user()
        t = topic(is_private=True)
        t.add_moderator(user.discussion)
        assert not user.discussion.is_subscribed_to(t)
        resp = user.post(url_for(self.endpoint, topic=t.name))
        assert user.discussion.is_subscribed_to(t)
        assert resp.status_code == http.HTTPStatus.OK

    def test_add_using_invalid_topic(self, api_user):
        user = api_user()
        resp = user.post(url_for(self.endpoint, topic="this-is-invalid"))
        assert resp.status_code == http.HTTPStatus.NOT_FOUND

    def test_remove(self, api_user, topic):
        user = api_user()
        t = topic()
        user.discussion.add_subscription(t)
        assert user.discussion.subscriptions == [t]
        resp = user.delete(url_for(self.endpoint, topic=t.name))
        assert resp.json == {}
        assert resp.status_code == http.HTTPStatus.OK
        assert user.discussion.subscriptions == []

    def test_remove_as_nonexistent_user(self, bad_auth_token_api_user, topic):
        user = bad_auth_token_api_user()
        t = topic()
        resp = user.delete(url_for(self.endpoint, topic=t.name))
        assert resp.status_code == http.HTTPStatus.UNAUTHORIZED

    def test_remove_leaves_moderation_status_unchanged(self, api_user, topic):
        user = api_user()
        t = topic()
        user.discussion.add_subscription(t)
        t.add_moderator(user.discussion)
        url = url_for(self.endpoint, topic=t.name)
        resp = user.delete(url)
        assert resp.status_code == http.HTTPStatus.OK
        assert user.discussion.is_moderator_of(t)

    def test_remove_using_invalid_topic(self, api_user):
        user = api_user()
        resp = user.delete(url_for(self.endpoint, topic="this-is-invalid"))
        assert resp.status_code == http.HTTPStatus.NOT_FOUND


class TestTopicSubscribeRequestApi:
    endpoint = "api_discussion_bp.topicsubscriberequestapi"

    def test_approve(self, api_user, topic):
        user1 = api_user(username="u1")
        user2 = api_user(username="u2")
        t = topic(is_private=True)
        t.add_moderator(user1.discussion)
        sr = user2.discussion.create_subscribe_request(t)
        resp2 = user1.put(url_for(self.endpoint, topic=t.name), json={"subscribe_request_id": sr.id})
        assert user2.discussion.is_subscribed_to(t)
        assert len(user2.discussion.topic_subscribe_requests) == 0
        assert resp2.json == {}
        assert resp2.status_code == http.HTTPStatus.OK

    def test_approve_if_invalid_subscribe_request_id(self, api_user, topic):
        user1 = api_user(username="u1")
        user2 = api_user(username="u2")
        t = topic(is_private=True)
        t.add_moderator(user1.discussion)
        sr = user2.discussion.create_subscribe_request(t)
        resp2 = user1.put(url_for(self.endpoint, topic=t.name), json={"subscribe_request_id": sr.id + 1})
        assert not user2.discussion.is_subscribed_to(t)
        assert len(user2.discussion.topic_subscribe_requests) == 1
        assert resp2.json == {}
        assert resp2.status_code == http.HTTPStatus.NOT_FOUND

    def test_approve_if_not_moderator(self, api_user, topic):
        user1 = api_user(username="u1")
        user2 = api_user(username="u2")
        t = topic(is_private=True)
        sr = user2.discussion.create_subscribe_request(t)
        resp2 = user1.put(url_for(self.endpoint, topic=t.name), json={"subscribe_request_id": sr.id})
        assert not user2.discussion.is_subscribed_to(t)
        assert len(user2.discussion.topic_subscribe_requests) == 1
        assert resp2.json == {}
        assert resp2.status_code == http.HTTPStatus.UNAUTHORIZED

    def test_create(self, api_user, topic):
        user = api_user()
        t = topic(is_private=True)
        assert len(user.discussion.topic_subscribe_requests) == 0
        resp = user.post(url_for(self.endpoint, topic=t.name))
        assert resp.json == {}
        assert resp.status_code == http.HTTPStatus.OK
        assert len(user.discussion.topic_subscribe_requests) == 1

    def test_create_as_nonexistent_user(self, bad_auth_token_api_user, topic):
        user = bad_auth_token_api_user()
        t = topic(is_private=True)
        resp = user.post(url_for(self.endpoint, topic=t.name))
        assert resp.status_code == http.HTTPStatus.UNAUTHORIZED

    def test_create_duplicate_request(self, api_user, topic):
        user = api_user()
        t = topic(is_private=True)
        user.post(url_for(self.endpoint, topic=t.name))
        assert len(user.discussion.topic_subscribe_requests) == 1
        sr = user.discussion.topic_subscribe_requests[0]
        user.post(url_for(self.endpoint, topic=t.name))
        assert user.discussion.topic_subscribe_requests == [sr]

    def test_create_if_is_not_private_topic(self, api_user, topic):
        user = api_user()
        t = topic()
        resp = user.post(url_for(self.endpoint, topic=t.name))
        assert len(user.discussion.topic_subscribe_requests) == 0
        assert resp.status_code == http.HTTPStatus.NOT_FOUND

    def test_create_using_invalid_topic(self, api_user):
        user = api_user()
        resp = user.post(url_for(self.endpoint, topic="this-is-invalid"))
        assert resp.status_code == http.HTTPStatus.NOT_FOUND

    def test_deny(self, api_user, topic):
        user1 = api_user(username="u1")
        user2 = api_user(username="u2")
        t = topic(is_private=True)
        t.add_moderator(user1.discussion)
        sr = user2.discussion.create_subscribe_request(t)
        resp2 = user1.delete(url_for(self.endpoint, topic=t.name), json={"subscribe_request_id": sr.id})
        assert not user2.discussion.is_subscribed_to(t)
        assert len(user2.discussion.topic_subscribe_requests) == 0
        assert resp2.json == {}
        assert resp2.status_code == http.HTTPStatus.OK

    def test_deny_if_invalid_subscribe_request_id(self, api_user, topic):
        user1 = api_user(username="u1")
        user2 = api_user(username="u2")
        t = topic(is_private=True)
        t.add_moderator(user1.discussion)
        sr = user2.discussion.create_subscribe_request(t)
        resp2 = user1.delete(url_for(self.endpoint, topic=t.name), json={"subscribe_request_id": sr.id + 1})
        assert not user2.discussion.is_subscribed_to(t)
        assert len(user2.discussion.topic_subscribe_requests) == 1
        assert resp2.json == {}
        assert resp2.status_code == http.HTTPStatus.NOT_FOUND

    def test_deny_if_not_moderator(self, api_user, topic):
        user1 = api_user(username="u1")
        user2 = api_user(username="u2")
        t = topic(is_private=True)
        sr = user2.discussion.create_subscribe_request(t)
        resp2 = user1.delete(url_for(self.endpoint, topic=t.name), json={"subscribe_request_id": sr.id})
        assert not user2.discussion.is_subscribed_to(t)
        assert len(user2.discussion.topic_subscribe_requests) == 1
        assert resp2.json == {}
        assert resp2.status_code == http.HTTPStatus.UNAUTHORIZED


@pytest.mark.parametrize(
    "action, vote_count",
    [
        ("downvote", 1),
        ("upvote", 1),
        ("delete", 0),
    ],
)
class TestCommentVoteApi:
    endpoint = "api_discussion_bp.commentvoteapi"

    def test_vote(self, comment, api_user, action, vote_count):
        user = api_user()
        c = comment(discussion=user.discussion)
        resp = user.post(url_for(self.endpoint, unique_id=c.unique_id), json={"action": action})
        assert resp.status_code == http.HTTPStatus.OK
        assert len(user.discussion.comment_votes) == vote_count
        assert len(c.votes) == vote_count

    def test_vote_as_nonexistent_user(self, comment, bad_auth_token_api_user, action, vote_count):
        user = bad_auth_token_api_user()
        c = comment(discussion=user.discussion)
        resp = user.post(url_for(self.endpoint, unique_id=c.unique_id), json={"action": action})
        assert resp.status_code == http.HTTPStatus.UNAUTHORIZED


@pytest.mark.parametrize(
    "action, vote_count",
    [
        ("downvote", 1),
        ("upvote", 1),
        ("delete", 0),
    ],
)
class TestThreadVoteApi:
    endpoint = "api_discussion_bp.threadvoteapi"

    def test_vote(self, api_user, thread, action, vote_count):
        user = api_user()
        t = thread(discussion=user.discussion)
        resp = user.post(url_for(self.endpoint, unique_id=t.unique_id), json={"action": action})
        assert resp.status_code == http.HTTPStatus.OK
        assert len(user.discussion.thread_votes) == vote_count
        assert len(t.votes) == vote_count

    def test_vote_as_nonexistent_user(self, bad_auth_token_api_user, thread, action, vote_count):
        user = bad_auth_token_api_user()
        t = thread(discussion=user.discussion)
        resp = user.post(url_for(self.endpoint, unique_id=t.unique_id), json={"action": action})
        assert resp.status_code == http.HTTPStatus.UNAUTHORIZED


@pytest.mark.parametrize(
    "action, obj_type",
    [
        ("downvote", "comment"),
        ("upvote", "comment"),
        ("delete", "comment"),
        ("downvote", "thread"),
        ("upvote", "thread"),
        ("delete", "thread"),
    ],
)
def test_vote_api_invalid_unique_id(api_user, action, obj_type):
    user = api_user()
    resp = user.post(
        url_for(f"api_discussion_bp.{obj_type}voteapi", unique_id="this-is-invalid"), json={"action": action}
    )
    assert resp.json == {}
    assert resp.status_code == http.HTTPStatus.NOT_FOUND
