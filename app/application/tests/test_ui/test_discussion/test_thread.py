from http import HTTPStatus

from flask import url_for

from application.models import Thread


def test_create_thread(topic, ui_user):
    user = ui_user()
    _topic = topic()
    resp = user.post(
        url_for("ui_bp.create_thread", topic=_topic.name),
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


def test_get_create_thread_page(topic, ui_user):
    t = topic()
    user = ui_user()
    url = url_for("ui_bp.create_thread", topic=t.name)
    resp = user.get(url)
    assert resp.request.base_url == url


def test_get_create_thread_page_if_unauthenticated(topic, client):
    t = topic()
    resp = client.get(url_for("ui_bp.create_thread", topic=t.name), follow_redirects=True)
    assert len(resp.history) == 1
    assert resp.request.base_url == url_for("ui_bp.login")


def test_view_thread(topic, ui_user):
    user = ui_user()
    _topic = topic()
    thread = _topic.create_thread(body="b", title="t", discussion=user.discussion)
    url = url_for(
        "ui_bp.view_thread",
        topic=_topic.name,
        thread_unique_id=thread.unique_id,
        slug=thread.slug,
    )
    resp = user.get(url)
    assert resp.request.base_url == url


def test_view_thread_that_does_not_exist(topic, ui_user):
    user = ui_user()
    _topic = topic()
    thread = _topic.create_thread(body="b", title="t", discussion=user.discussion)
    resp = user.get(
        url_for(
            "ui_bp.view_thread",
            topic=_topic.name,
            thread_unique_id="this-in-invalid",
            slug=thread.slug,
        ),
    )
    assert resp.status_code == HTTPStatus.NOT_FOUND
