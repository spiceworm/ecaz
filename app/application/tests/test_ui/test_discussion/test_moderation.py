from flask import url_for

from application.constants import messages
from application.ui import forms


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


class TestModerationTopicBans:
    endpoint = "ui_bp.moderation_topic_bans"

    def test_create_ban(self, topic, ui_user):
        u1 = ui_user()
        u2 = ui_user()
        t = topic(moderators=[u1.discussion])
        url = url_for(self.endpoint, topic=t.name)
        form = forms.CreateTopicBanForm()
        resp = u1.post(
            url,
            data={
                "expires_at_number": 0,
                "expires_at_unit": form.EXPIRES_NEVER,
                "is_shadow": False,
                "reason": "testing",
                "username": u2.username,
            },
        )
        assert u2.discussion.is_banned_from(t)
        assert resp.request.base_url == url

    def test_create_ban_if_invalid_username(self, topic, ui_user):
        u1 = ui_user()
        u2 = ui_user()
        t = topic(moderators=[u1.discussion])
        url = url_for(self.endpoint, topic=t.name)
        form = forms.CreateTopicBanForm()
        resp = u1.post(
            url,
            data={
                "expires_at_number": 0,
                "expires_at_unit": form.EXPIRES_NEVER,
                "is_shadow": False,
                "reason": "testing",
                "username": "this-is-invalid",
            },
        )
        assert messages.NO_USER_FOR_PROVIDED_USERNAME in resp.data.decode()
        assert resp.request.base_url == url

    def test_create_duplicate_ban(self, topic, ui_user):
        u1 = ui_user()
        u2 = ui_user()
        t = topic(moderators=[u1.discussion])
        t.create_ban(created_by=u1.discussion, discussion=u2.discussion, reason="testing")
        url = url_for(self.endpoint, topic=t.name)
        form = forms.CreateTopicBanForm()
        resp = u1.post(
            url,
            data={
                "expires_at_number": 0,
                "expires_at_unit": form.EXPIRES_NEVER,
                "is_shadow": False,
                "reason": "testing",
                "username": u2.username,
            },
        )
        assert messages.BAN_ALREADY_EXISTS_FOR_USER in resp.data.decode()
        assert resp.request.base_url == url

    def test_create_temporary_ban(self, topic, ui_user):
        u1 = ui_user()
        u2 = ui_user()
        t = topic(moderators=[u1.discussion])
        url = url_for(self.endpoint, topic=t.name)
        form = forms.CreateTopicBanForm()
        resp = u1.post(
            url,
            data={
                "expires_at_number": 1,
                "expires_at_unit": form.EXPIRES_UNIT_WEEKS,
                "is_shadow": False,
                "reason": "testing",
                "username": u2.username,
            },
        )
        assert u2.discussion.is_banned_from(t)
        assert u2.discussion.bans[0].expires_at is not None
        assert resp.request.base_url == url

    def test_get(self, topic, ui_user):
        u = ui_user()
        t = topic(moderators=[u.discussion])
        url = url_for(self.endpoint, topic=t.name)
        resp = u.get(url)
        assert resp.request.base_url == url

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


class TestModerationTopicSubscribeRequests:
    endpoint = "ui_bp.moderation_topic_subscribe_requests"

    def test_get(self, topic, ui_user):
        u = ui_user()
        t = topic(moderators=[u.discussion])
        url = url_for(self.endpoint, topic=t.name)
        resp = u.get(url)
        assert resp.request.base_url == url

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
