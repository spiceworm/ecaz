import http

from flask import url_for
import pytest


def test_delete_comment(api_user, topic):
    user = api_user()
    _topic = topic()
    thread = _topic.create_thread(body="b1", title="t", discussion=user.discussion)
    comment = thread.create_comment(body="b2", discussion=user.discussion)
    resp = user.delete(url_for("api_discussion_bp.commentapi", unique_id=comment.unique_id))
    assert resp.status_code == http.HTTPStatus.OK
    assert comment.is_deleted


def test_delete_comment_created_by_different_user(api_user, topic, user):
    user1 = api_user(email="1@test.com")
    user2 = user(email="2@tets.com")
    _topic = topic()
    thread = _topic.create_thread(title="t", body="b1", discussion=user1.discussion)
    comment = thread.create_comment(body="b2", discussion=user2.discussion)
    resp = user1.delete(url_for("api_discussion_bp.commentapi", unique_id=comment.unique_id))
    assert resp.status_code == http.HTTPStatus.NOT_FOUND
    assert not comment.is_deleted


def test_delete_thread(api_user, topic):
    user = api_user()
    _topic = topic()
    thread = _topic.create_thread(body="b1", title="t", discussion=user.discussion)
    resp = user.delete(url_for("api_discussion_bp.threadapi", unique_id=thread.unique_id))
    assert resp.status_code == http.HTTPStatus.OK
    assert thread.is_deleted


def test_delete_thread_created_by_different_user(api_user, topic, user):
    user1 = api_user(email="1@test.com")
    user2 = user(email="2@tets.com")
    _topic = topic()
    thread = _topic.create_thread(title="t", body="b1", discussion=user2.discussion)
    resp = user1.delete(url_for("api_discussion_bp.threadapi", unique_id=thread.unique_id))
    assert resp.status_code == http.HTTPStatus.NOT_FOUND
    assert not thread.is_deleted


def test_get_comment_top_level(client, topic, user):
    u = user()
    _topic = topic()
    thread = _topic.create_thread(title="t", body="b1", discussion=u.discussion)
    comment = thread.create_comment(body="b2", discussion=u.discussion)
    resp = client.get(url_for("api_discussion_bp.commentapi", unique_id=comment.unique_id))
    assert resp.json == {
        'body': comment.body,
        'created_at': comment.created_at.isoformat(),
        'discussion': {
            'user': {
                'created_at': comment.discussion.user.created_at.isoformat(),
                'username': comment.discussion.user.username
            }
        },
        "parent": None,
        'thread': {
            'created_at': comment.thread.created_at.isoformat(),
            'discussion': {
                'user': {
                    'created_at': thread.discussion.user.created_at.isoformat(),
                    'username': thread.discussion.user.username
                }
            },
            'topic': {
                'created_at': thread.topic.created_at.isoformat(),
                'name': thread.topic.name,
            },
            'title': thread.title,
            'unique_id': thread.unique_id
        },
        'unique_id': comment.unique_id
    }


def test_get_comment_nested(client, topic, user):
    u = user()
    _topic = topic()
    thread = _topic.create_thread(title="t", body="b1", discussion=u.discussion)
    parent_comment = thread.create_comment(body="b2", discussion=u.discussion)
    nested_comment = parent_comment.create_comment(body="b3", discussion=u.discussion)
    resp = client.get(url_for("api_discussion_bp.commentapi", unique_id=nested_comment.unique_id))
    assert resp.json == {
        'body': nested_comment.body,
        'created_at': nested_comment.created_at.isoformat(),
        'discussion': {
            'user': {
                'created_at': nested_comment.discussion.user.created_at.isoformat(),
                'username': nested_comment.discussion.user.username
            }
        },
        "parent": {
            'body': parent_comment.body,
            'created_at': parent_comment.created_at.isoformat(),
            'discussion': {
                'user': {
                    'created_at': parent_comment.discussion.user.created_at.isoformat(),
                    'username': parent_comment.discussion.user.username
                }
            },
            "parent": None,
            "unique_id": parent_comment.unique_id,
        },
        'thread': {
            'created_at': nested_comment.thread.created_at.isoformat(),
            'discussion': {
                'user': {
                    'created_at': nested_comment.thread.discussion.user.created_at.isoformat(),
                    'username': nested_comment.thread.discussion.user.username
                }
            },
            'topic': {
                'created_at': nested_comment.thread.topic.created_at.isoformat(),
                'name': nested_comment.thread.topic.name,
            },
            'title': nested_comment.thread.title,
            'unique_id': nested_comment.thread.unique_id
        },
        'unique_id': nested_comment.unique_id
    }


def test_get_comment_using_invalid_unique_id(client):
    resp = client.get(url_for("api_discussion_bp.commentapi", unique_id="this-is-invalid"))
    assert resp.status_code == http.HTTPStatus.NOT_FOUND


def test_get_thread(client, topic, user):
    u = user()
    _topic = topic()
    thread = _topic.create_thread(title="t", body="b", discussion=u.discussion)
    resp = client.get(url_for("api_discussion_bp.threadapi", unique_id=thread.unique_id))
    assert resp.json == {
        'created_at': thread.created_at.isoformat(),
        'discussion': {
            'user': {
                'created_at': thread.discussion.user.created_at.isoformat(),
                'username': thread.discussion.user.username
            }
        },
        'topic': {
            'created_at': thread.topic.created_at.isoformat(),
            'name': thread.topic.name
        },
        'title': thread.title,
        'unique_id': thread.unique_id
    }


def test_get_thread_using_invalid_unique_id(client):
    resp = client.get(url_for("api_discussion_bp.threadapi", unique_id="this-is-invalid"))
    assert resp.status_code == http.HTTPStatus.NOT_FOUND


def test_get_topic(client, topic):
    _topic = topic()
    resp = client.get(url_for("api_discussion_bp.topicapi", topic=_topic.name))
    assert resp.json == {
        'created_at': _topic.created_at.isoformat(),
        'name': _topic.name
    }


def test_get_topic_using_invalid_name(client):
    resp = client.get(url_for("api_discussion_bp.topicapi", topic="this-is-invalid"))
    assert resp.status_code == http.HTTPStatus.NOT_FOUND


@pytest.mark.parametrize(
    "action, vote_count",
    [
        ("downvote", 1),
        ("upvote", 1),
        ("delete", 0),
    ],
)
class TestVoteApi:
    def test_comment_vote_api(self, topic, api_user, action, vote_count):
        user = api_user()
        _topic = topic()
        thread = _topic.create_thread(title="t", body="b", discussion=user.discussion)
        comment = thread.create_comment(body="b", discussion=user.discussion)
        resp = user.post(
            url_for("api_discussion_bp.commentvoteapi", unique_id=comment.unique_id),
            json={"action": action}
        )
        assert resp.json == {"success": "processed"}
        assert len(user.discussion.comment_votes) == vote_count
        assert len(comment.votes) == vote_count

    def test_thread_vote_api(self, topic, api_user, action, vote_count):
        user = api_user()
        _topic = topic()
        thread = _topic.create_thread(title="t", body="b", discussion=user.discussion)
        resp = user.post(
            url_for("api_discussion_bp.threadvoteapi", unique_id=thread.unique_id),
            json={"action": action}
        )
        assert resp.json == {"success": "processed"}
        assert len(user.discussion.thread_votes) == vote_count
        assert len(thread.votes) == vote_count


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
        url_for(f"api_discussion_bp.{obj_type}voteapi", unique_id="this-is-invalid"),
        json={"action": action}
    )
    assert resp.json == {}
    assert resp.status_code == http.HTTPStatus.NOT_FOUND
