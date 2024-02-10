from flask import url_for


def test_get_moderation_home(topic, ui_user):
    user = ui_user()
    t = topic(is_private=True)
    t.add_moderator(user.discussion)
    url = url_for("ui_bp.moderation_home")
    resp = user.get(url)
    assert resp.request.base_url == url


def test_get_moderation_home_if_not_moderator(ui_user):
    user = ui_user()
    url = url_for("ui_bp.moderation_home")
    resp = user.get(url, follow_redirects=True)
    assert len(resp.history) == 1
    assert resp.request.base_url == url_for("ui_bp.profile")


def test_get_moderation_home_if_unauthenticated(client):
    url = url_for("ui_bp.moderation_home")
    resp = client.get(url, follow_redirects=True)
    assert len(resp.history) == 1
    assert resp.request.base_url == url_for("ui_bp.login")


def test_get_moderation_topic(topic, ui_user):
    user = ui_user()
    t = topic()
    t.add_moderator(user.discussion)
    url = url_for("ui_bp.moderation_topic", topic=t.name)
    resp = user.get(url)
    assert resp.request.base_url == url


def test_get_moderation_topic_if_not_moderator(topic, ui_user):
    user = ui_user()
    t = topic()
    url = url_for("ui_bp.moderation_topic", topic=t.name)
    resp = user.get(url, follow_redirects=True)
    assert len(resp.history) == 1
    assert resp.request.base_url == url_for("ui_bp.profile")


def test_get_moderation_topic_if_not_moderator_of_topic(topic, ui_user):
    user = ui_user()
    t1 = topic(name="t1")
    t2 = topic(name="t2")
    t1.add_moderator(user.discussion)
    url = url_for("ui_bp.moderation_topic", topic=t2.name)
    resp = user.get(url, follow_redirects=True)
    assert len(resp.history) == 1
    assert resp.request.base_url == url_for("ui_bp.profile")


def test_get_moderation_topic_if_topic_does_not_exist(topic, ui_user):
    user = ui_user()
    t = topic()
    t.add_moderator(user.discussion)
    url = url_for("ui_bp.moderation_topic", topic="does-not-exist")
    resp = user.get(url, follow_redirects=True)
    assert len(resp.history) == 1
    assert resp.request.base_url == url_for("ui_bp.profile")
