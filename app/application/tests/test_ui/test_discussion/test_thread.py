from http import HTTPStatus

from flask import url_for

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
