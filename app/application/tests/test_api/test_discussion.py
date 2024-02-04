import http

from flask import url_for
import pytest


def test_delete_comment(api_user, comment):
    user = api_user()
    c = comment(discussion=user.discussion)
    resp = user.delete(url_for("api_discussion_bp.commentapi", unique_id=c.unique_id))
    assert resp.status_code == http.HTTPStatus.OK
    assert c.is_deleted


def test_delete_comment_created_by_different_user(api_user, comment, user):
    user1 = api_user(email="1@test.com")
    user2 = user(email="2@tets.com")
    c = comment(discussion=user2.discussion)
    resp = user1.delete(url_for("api_discussion_bp.commentapi", unique_id=c.unique_id))
    assert resp.status_code == http.HTTPStatus.NOT_FOUND
    assert not c.is_deleted


def test_delete_thread(api_user, thread):
    user = api_user()
    t = thread(discussion=user.discussion)
    resp = user.delete(url_for("api_discussion_bp.threadapi", unique_id=t.unique_id))
    assert resp.status_code == http.HTTPStatus.OK
    assert t.is_deleted


def test_delete_thread_created_by_different_user(api_user, thread):
    user1 = api_user(email="1@test.com")
    user2 = api_user(email="2@tets.com")
    t = thread(discussion=user2.discussion)
    resp = user1.delete(url_for("api_discussion_bp.threadapi", unique_id=t.unique_id))
    assert resp.status_code == http.HTTPStatus.NOT_FOUND
    assert not t.is_deleted


def test_edit_comment_body(api_user, comment):
    u = api_user()
    c = comment(discussion=u.discussion)
    updated_body = "This is the updated comment body string"
    assert c.body != updated_body
    resp = u.post(
        url_for("api_discussion_bp.commentapi", unique_id=c.unique_id),
        json={"body": updated_body},
    )
    assert resp.json["body"] == updated_body
    assert c.body == updated_body
    assert resp.status_code == http.HTTPStatus.OK


def test_edit_comment_body_created_by_different_user(api_user, comment):
    u1 = api_user(email="1@test.com")
    u2 = api_user(email="2@test.com")
    c = comment(discussion=u1.discussion)
    updated_body = "This is the updated comment body string but no update should occur"
    assert c.body != updated_body
    resp = u2.post(
        url_for("api_discussion_bp.commentapi", unique_id=c.unique_id),
        json={"body": updated_body},
    )
    assert resp.json == {}
    assert c.body != updated_body
    assert resp.status_code == http.HTTPStatus.NOT_FOUND


def test_get_comment_top_level(comment, client, user):
    u = user()
    c = comment(discussion=u.discussion)
    resp = client.get(url_for("api_discussion_bp.commentapi", unique_id=c.unique_id))
    assert resp.json == {
        "body": c.body,
        "created_at": c.created_at.isoformat(),
        "discussion": {
            "user": {"created_at": c.discussion.user.created_at.isoformat(), "username": c.discussion.user.username}
        },
        "parent": None,
        "thread": {
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


def test_get_comment_nested(comment, client, user):
    u = user()
    parent_comment = comment(discussion=u.discussion)
    nested_comment = parent_comment.create_comment(body="b", discussion=u.discussion)
    resp = client.get(url_for("api_discussion_bp.commentapi", unique_id=nested_comment.unique_id))
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


def test_get_comment_using_invalid_unique_id(client):
    resp = client.get(url_for("api_discussion_bp.commentapi", unique_id="this-is-invalid"))
    assert resp.status_code == http.HTTPStatus.NOT_FOUND


def test_get_thread(client, thread, user):
    u = user()
    t = thread(discussion=u.discussion)
    resp = client.get(url_for("api_discussion_bp.threadapi", unique_id=t.unique_id))
    assert resp.json == {
        "created_at": t.created_at.isoformat(),
        "discussion": {
            "user": {"created_at": t.discussion.user.created_at.isoformat(), "username": t.discussion.user.username}
        },
        "topic": {"created_at": t.topic.created_at.isoformat(), "name": t.topic.name},
        "title": t.title,
        "unique_id": t.unique_id,
    }


def test_get_thread_using_invalid_unique_id(client):
    resp = client.get(url_for("api_discussion_bp.threadapi", unique_id="this-is-invalid"))
    assert resp.status_code == http.HTTPStatus.NOT_FOUND


def test_get_topic(client, topic):
    _topic = topic()
    resp = client.get(url_for("api_discussion_bp.topicapi", topic=_topic.name))
    assert resp.json == {"created_at": _topic.created_at.isoformat(), "name": _topic.name}


def test_get_topic_using_invalid_name(client):
    resp = client.get(url_for("api_discussion_bp.topicapi", topic="this-is-invalid"))
    assert resp.status_code == http.HTTPStatus.NOT_FOUND


class TestSaveApi:
    def test_save_comment(self, comment, api_user):
        user = api_user()
        c = comment(discussion=user.discussion)
        url = url_for("api_discussion_bp.commentsaveapi", unique_id=c.unique_id)

        resp1 = user.post(url)
        assert resp1.status_code == http.HTTPStatus.OK
        assert user.discussion.saved_comments == [c]

        resp2 = user.delete(url)
        assert resp2.status_code == http.HTTPStatus.OK
        assert user.discussion.saved_comments == []

    def test_save_thread(self, thread, api_user):
        user = api_user()
        t = thread(discussion=user.discussion)
        url = url_for("api_discussion_bp.threadsaveapi", unique_id=t.unique_id)

        resp1 = user.post(url)
        assert resp1.status_code == http.HTTPStatus.OK
        assert user.discussion.saved_threads == [t]

        resp2 = user.delete(url)
        assert resp2.status_code == http.HTTPStatus.OK
        assert user.discussion.saved_threads == []


@pytest.mark.parametrize(
    "action, vote_count",
    [
        ("downvote", 1),
        ("upvote", 1),
        ("delete", 0),
    ],
)
class TestVoteApi:
    def test_comment_vote_api(self, comment, api_user, action, vote_count):
        user = api_user()
        c = comment(discussion=user.discussion)
        resp = user.post(url_for("api_discussion_bp.commentvoteapi", unique_id=c.unique_id), json={"action": action})
        assert resp.status_code == http.HTTPStatus.OK
        assert len(user.discussion.comment_votes) == vote_count
        assert len(c.votes) == vote_count

    def test_thread_vote_api(self, api_user, thread, action, vote_count):
        user = api_user()
        t = thread(discussion=user.discussion)
        resp = user.post(url_for("api_discussion_bp.threadvoteapi", unique_id=t.unique_id), json={"action": action})
        assert resp.status_code == http.HTTPStatus.OK
        assert len(user.discussion.thread_votes) == vote_count
        assert len(t.votes) == vote_count


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
