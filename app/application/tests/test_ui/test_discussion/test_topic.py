from http import HTTPStatus

from flask import url_for
import pytest

from application.constants import messages
from application.models import Topic


def test_create_topic(ui_user):
    user = ui_user()
    topic_name = "Topic"
    topic_desc = "Description"
    resp = user.post(
        url_for("ui_bp.create_topic"),
        data={"name": topic_name, "description": topic_desc},
        follow_redirects=True,
    )
    topic = Topic.query.filter_by(name=topic_name).one_or_none()
    assert len(resp.history) == 1
    assert resp.request.base_url == url_for("ui_bp.view_topic", topic=topic_name)
    assert topic.name == topic_name
    assert topic.description == topic_desc
    assert user.discussion.is_moderator_of(topic)


def test_create_topic_duplicate_topic(topic, ui_user):
    user = ui_user()
    _topic = topic()
    resp = user.post(
        url_for("ui_bp.create_topic"),
        data={"name": _topic.name, "description": "description"},
    )
    assert messages.TOPIC_ALREADY_EXISTS in resp.data.decode()


@pytest.mark.parametrize(
    "topic_name",
    [
        " invalid topic",
        "this is invalid",
        " this is also invalid ",
    ],
)
def test_create_topic_fails_if_contains_whitespace(ui_user, topic_name):
    user = ui_user()
    resp = user.post(
        url_for("ui_bp.create_topic"),
        data={"name": topic_name, "description": "description"},
        follow_redirects=True,
    )
    assert messages.WHITESPACE_NOT_ALLOWED in resp.data.decode()


def test_get_create_topic_page(ui_user):
    user = ui_user()
    url = url_for("ui_bp.create_topic")
    resp = user.get(url)
    assert resp.request.base_url == url


def test_get_create_topic_page_if_unauthenticated(client):
    resp = client.get(url_for("ui_bp.create_topic"), follow_redirects=True)
    assert len(resp.history) == 1
    assert resp.request.base_url == url_for("ui_bp.login")


def test_view_topic(topic, ui_user):
    user = ui_user()
    _topic = topic()
    url = url_for("ui_bp.view_topic", topic=_topic.name)
    resp = user.get(url)
    assert resp.request.base_url == url


def test_view_topic_if_is_private_and_is_authenticated(topic, ui_user):
    user = ui_user()
    _topic = topic(is_private=True)
    resp = user.get(url_for("ui_bp.view_topic", topic=_topic.name))
    assert "This topic is private" in resp.data.decode()


def test_view_topic_if_is_private_and_is_moderator(topic, ui_user):
    user = ui_user()
    _topic = topic(is_private=True)
    thread = _topic.create_thread(body="b", title="This is the title", discussion=user.discussion)
    _topic.add_moderator(user.discussion)
    resp = user.get(url_for("ui_bp.view_topic", topic=_topic.name))
    assert thread.title in resp.data.decode()


def test_view_topic_if_is_private_and_is_subscribed(topic, ui_user):
    user = ui_user()
    _topic = topic(is_private=True)
    thread = _topic.create_thread(body="b", title="This is the title", discussion=user.discussion)
    user.discussion.add_subscription(_topic)
    resp = user.get(url_for("ui_bp.view_topic", topic=_topic.name))
    assert thread.title in resp.data.decode()


def test_view_topic_if_is_private_and_is_unauthenticated(client, topic):
    _topic = topic(is_private=True)
    resp = client.get(url_for("ui_bp.view_topic", topic=_topic.name))
    assert "This topic is private" in resp.data.decode()


def test_view_topic_that_does_not_exist(ui_user):
    user = ui_user()
    resp = user.get(url_for("ui_bp.view_topic", topic="does-not-exist"))
    assert resp.status_code == HTTPStatus.NOT_FOUND
