from http import HTTPStatus

from flask import url_for

from application.constants import messages
from application.models import Thread


class TestCreateThread:
    endpoint = "ui_bp.create_thread"

    def test_create(self, topic, ui_user):
        user = ui_user()
        _topic = topic()
        resp = user.post(
            url_for(self.endpoint, topic=_topic.name),
            data={"body": "Body", "title": "Title"},
            follow_redirects=True,
        )
        thread = Thread.query.first()
        assert resp.request.base_url == url_for(
            "ui_bp.view_thread",
            topic=_topic.name,
            thread_unique_id=thread.unique_id,
            slug=thread.slug,
        )

    def test_create_if_banned(self, topic, ui_user):
        u1 = ui_user()
        u2 = ui_user()
        _topic = topic(moderators=[u1.discussion])
        _topic.create_ban(created_by=u1.discussion, discussion=u2.discussion, reason="testing")
        assert u2.discussion.is_banned_from(_topic)
        url = url_for(self.endpoint, topic=_topic.name)
        resp = u2.post(
            url,
            data={"body": "Body", "title": "Title"},
            follow_redirects=True,
        )
        assert messages.BANNED_FROM_CONTRIBUTING in resp.data.decode()
        assert not u2.discussion.threads
        assert resp.request.base_url == url

    def test_create_if_shadow_banned(self, topic, ui_user):
        u1 = ui_user()
        u2 = ui_user()
        _topic = topic(moderators=[u1.discussion])
        _topic.create_ban(created_by=u1.discussion, discussion=u2.discussion, reason="testing", is_shadow=True)
        assert u2.discussion.is_banned_from(_topic)
        url = url_for(self.endpoint, topic=_topic.name)
        resp = u2.post(
            url,
            data={"body": "Body", "title": "A unique title for the thread"},
            follow_redirects=True,
        )
        thread = Thread.query.first()
        assert resp.request.base_url == url_for(
            "ui_bp.view_thread",
            topic=_topic.name,
            thread_unique_id=thread.unique_id,
            slug=thread.slug,
        )

    def test_get(self, topic, ui_user):
        t = topic()
        user = ui_user()
        url = url_for(self.endpoint, topic=t.name)
        resp = user.get(url)
        assert resp.request.base_url == url

    def test_get_if_unauthenticated(self, topic, client):
        t = topic()
        resp = client.get(url_for(self.endpoint, topic=t.name), follow_redirects=True)
        assert len(resp.history) == 1
        assert resp.request.base_url == url_for("ui_bp.login")


class TestViewThread:
    endpoint = "ui_bp.view_thread"

    def test_view(self, thread, ui_user):
        user = ui_user()
        t = thread(discussion=user.discussion)
        url = url_for(
            self.endpoint,
            topic=t.topic.name,
            thread_unique_id=t.unique_id,
            slug=t.slug,
        )
        resp = user.get(url)
        assert resp.request.base_url == url

    def test_view_if_does_not_exist(self, thread, ui_user):
        user = ui_user()
        t = thread(discussion=user.discussion)
        resp = user.get(
            url_for(
                self.endpoint,
                topic=t.topic.name,
                thread_unique_id="this-in-invalid",
                slug=t.slug,
            ),
        )
        assert resp.status_code == HTTPStatus.NOT_FOUND

    def test_view_as_creator_of_hidden_comment(self, comment, ui_user):
        u = ui_user()
        c = comment(body="unique text for the comment body", discussion=u.discussion, is_hidden=True)
        url = url_for(
            self.endpoint,
            topic=c.thread.topic.name,
            thread_unique_id=c.thread.unique_id,
            slug=c.thread.slug,
        )
        resp = u.get(url)
        assert c.body in resp.data.decode()

    def test_view_as_authenticated_noncreator_of_hidden_comment(self, comment, ui_user):
        u1 = ui_user()
        u2 = ui_user()
        c = comment(body="unique text for the comment body", discussion=u1.discussion, is_hidden=True)
        url = url_for(
            self.endpoint,
            topic=c.thread.topic.name,
            thread_unique_id=c.thread.unique_id,
            slug=c.thread.slug,
        )
        resp = u2.get(url)
        assert c.body not in resp.data.decode()

    def test_view_as_unauthenticated_noncreator_of_hidden_comment(self, client, comment, user):
        u = user()
        c = comment(body="unique text for the comment body", discussion=u.discussion, is_hidden=True)
        url = url_for(
            self.endpoint,
            topic=c.thread.topic.name,
            thread_unique_id=c.thread.unique_id,
            slug=c.thread.slug,
        )
        resp = client.get(url)
        assert c.body not in resp.data.decode()
