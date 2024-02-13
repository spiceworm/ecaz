from http import HTTPStatus

from flask import url_for
import pytest

from application.constants import messages
from application.models import Topic


class TestCreateTopic:
    endpoint = "ui_bp.create_topic"

    def test_create(self, ui_user):
        user = ui_user()
        topic_name = "Topic"
        topic_desc = "Description"
        resp = user.post(
            url_for(self.endpoint),
            data={"name": topic_name, "description": topic_desc},
            follow_redirects=True,
        )
        topic = Topic.query.filter_by(name=topic_name).one_or_none()
        assert len(resp.history) == 1
        assert resp.request.base_url == url_for("ui_bp.view_topic", topic=topic_name)
        assert topic.name == topic_name
        assert topic.description == topic_desc
        assert user.discussion.is_moderator_of(topic)

    def test_create_duplicate_topic(self, topic, ui_user):
        user = ui_user()
        _topic = topic()
        resp = user.post(
            url_for(self.endpoint),
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
    def test_create_fails_if_contains_whitespace(self, ui_user, topic_name):
        user = ui_user()
        resp = user.post(
            url_for(self.endpoint),
            data={"name": topic_name, "description": "description"},
            follow_redirects=True,
        )
        assert messages.WHITESPACE_NOT_ALLOWED in resp.data.decode()

    def test_get(self, ui_user):
        user = ui_user()
        url = url_for(self.endpoint)
        resp = user.get(url)
        assert resp.request.base_url == url

    def test_get_if_unauthenticated(self, client):
        resp = client.get(url_for(self.endpoint), follow_redirects=True)
        assert len(resp.history) == 1
        assert resp.request.base_url == url_for("ui_bp.login")


class TestViewTopic:
    endpoint = "ui_bp.view_topic"

    def test_view_topic(self, topic, ui_user):
        user = ui_user()
        _topic = topic()
        url = url_for(self.endpoint, topic=_topic.name)
        resp = user.get(url)
        assert resp.request.base_url == url

    def test_view_if_is_private_and_is_authenticated(self, topic, ui_user):
        user = ui_user()
        _topic = topic(is_private=True)
        resp = user.get(url_for(self.endpoint, topic=_topic.name))
        assert "This topic is private" in resp.data.decode()

    def test_view_if_is_private_and_is_moderator(self, topic, ui_user):
        user = ui_user()
        _topic = topic(is_private=True)
        thread = _topic.create_thread(body="b", title="This is the title", discussion=user.discussion)
        _topic.add_moderator(user.discussion)
        resp = user.get(url_for(self.endpoint, topic=_topic.name))
        assert thread.title in resp.data.decode()

    def test_view_if_is_private_and_is_subscribed(self, topic, ui_user):
        user = ui_user()
        _topic = topic(is_private=True)
        thread = _topic.create_thread(body="b", title="This is the title", discussion=user.discussion)
        user.discussion.add_subscription(_topic)
        resp = user.get(url_for(self.endpoint, topic=_topic.name))
        assert thread.title in resp.data.decode()

    def test_view_if_is_private_and_is_unauthenticated(self, client, topic):
        _topic = topic(is_private=True)
        resp = client.get(url_for(self.endpoint, topic=_topic.name))
        assert "This topic is private" in resp.data.decode()

    def test_view_if_does_not_exist(self, ui_user):
        user = ui_user()
        resp = user.get(url_for(self.endpoint, topic="does-not-exist"))
        assert resp.status_code == HTTPStatus.NOT_FOUND

    def test_view_as_creator_of_hidden_thread(self, topic, ui_user):
        u = ui_user()
        _topic = topic()
        thread = _topic.create_thread(
            title="a unique title for the thread", body="b", discussion=u.discussion, is_hidden=True
        )
        resp = u.get(url_for(self.endpoint, topic=_topic.name))
        assert thread.title in resp.data.decode()

    def test_view_as_authenticated_noncreator_of_hidden_thread(self, topic, ui_user):
        u1 = ui_user()
        u2 = ui_user()
        _topic = topic()
        thread = _topic.create_thread(
            title="a unique title for the thread", body="b", discussion=u1.discussion, is_hidden=True
        )
        resp = u2.get(url_for(self.endpoint, topic=_topic.name))
        assert thread.title not in resp.data.decode()

    def test_view_as_unauthenticated_noncreator_of_hidden_thread(self, client, topic, user):
        u = user()
        _topic = topic()
        thread = _topic.create_thread(
            title="a unique title for the thread", body="b", discussion=u.discussion, is_hidden=True
        )
        resp = client.get(url_for(self.endpoint, topic=_topic.name))
        assert thread.title not in resp.data.decode()
