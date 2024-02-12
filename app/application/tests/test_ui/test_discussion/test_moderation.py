from flask import url_for


class TestModerationHome:
    endpoint = "ui_bp.moderation_home"

    def test_get(self, topic, ui_user):
        user = ui_user()
        topic(moderators=[user.discussion])
        url = url_for(self.endpoint)
        resp = user.get(url)
        assert resp.request.base_url == url

    def test_get_if_not_moderator(self, ui_user):
        user = ui_user()
        url = url_for(self.endpoint)
        resp = user.get(url, follow_redirects=True)
        assert len(resp.history) == 1
        assert resp.request.base_url == url_for("ui_bp.profile")

    def test_get_if_unauthenticated(self, client):
        url = url_for(self.endpoint)
        resp = client.get(url, follow_redirects=True)
        assert len(resp.history) == 1
        assert resp.request.base_url == url_for("ui_bp.login")


class TestModerationTopic:
    endpoint = "ui_bp.moderation_topic"

    def test_get(self, topic, ui_user):
        user = ui_user()
        t = topic(moderators=[user.discussion])
        url = url_for(self.endpoint, topic=t.name)
        resp = user.get(url)
        assert resp.request.base_url == url

    def test_get_if_not_moderator(self, topic, ui_user):
        user = ui_user()
        t = topic()
        url = url_for(self.endpoint, topic=t.name)
        resp = user.get(url, follow_redirects=True)
        assert len(resp.history) == 1
        assert resp.request.base_url == url_for("ui_bp.profile")

    def test_get_if_not_moderator_of_topic(self, topic, ui_user):
        user = ui_user()
        topic(name="t1", moderators=[user.discussion])
        t = topic(name="t2")
        url = url_for(self.endpoint, topic=t.name)
        resp = user.get(url, follow_redirects=True)
        assert len(resp.history) == 1
        assert resp.request.base_url == url_for("ui_bp.profile")

    def test_get_if_topic_does_not_exist(self, topic, ui_user):
        user = ui_user()
        topic(moderators=[user.discussion])
        url = url_for(self.endpoint, topic="does-not-exist")
        resp = user.get(url, follow_redirects=True)
        assert len(resp.history) == 1
        assert resp.request.base_url == url_for("ui_bp.profile")
