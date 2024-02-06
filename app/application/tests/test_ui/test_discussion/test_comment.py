import http

import flask
from flask import url_for

from application.models import Comment


def test_create_top_level_comment(thread, ui_user):
    user = ui_user()
    t = thread(body="b", title="t", discussion=user.discussion)
    resp = user.post(
        url_for(
            "ui_bp.create_comment",
            topic=t.topic.name,
            thread_unique_id=t.unique_id,
            slug=t.slug,
            parent_unique_id=t.unique_id,
        ),
        data={"body": "comment"},
        follow_redirects=True,
    )
    assert len(resp.history) == 1
    assert resp.request.base_url == url_for(
        "ui_bp.view_thread",
        topic=t.topic.name,
        thread_unique_id=t.unique_id,
        slug=t.slug,
    )


def test_create_nested_comment(comment, ui_user):
    user = ui_user()
    d = user.discussion
    parent_comment = comment(discussion=d)
    child_comment_body = "this the child comment"
    resp = user.post(
        url_for(
            "ui_bp.create_comment",
            topic=parent_comment.thread.topic.name,
            thread_unique_id=parent_comment.thread.unique_id,
            slug=parent_comment.thread.slug,
            parent_unique_id=parent_comment.unique_id,
        ),
        data={"body": child_comment_body},
        follow_redirects=True,
    )
    child_comment = Comment.query.filter_by(body=child_comment_body).one()
    assert child_comment.parent is parent_comment
    assert len(resp.history) == 1
    assert resp.request.base_url == url_for(
        "ui_bp.view_thread",
        topic=parent_comment.thread.topic.name,
        thread_unique_id=parent_comment.thread.unique_id,
        slug=parent_comment.thread.slug,
    )


def test_view_permalinked_comment(comment, ui_user):
    user = ui_user()
    c = comment(discussion=user.discussion)
    url = flask.url_for(
        "ui_bp.view_comment",
        topic=c.thread.topic.name,
        thread_unique_id=c.thread.unique_id,
        slug=c.thread.slug,
        comment_unique_id=c.unique_id,
    )
    resp = user.get(url)
    assert resp.request.base_url == url


def test_view_permalinked_comment_that_does_not_exist(thread, ui_user):
    user = ui_user()
    t = thread(discussion=user.discussion)
    url = flask.url_for(
        "ui_bp.view_comment",
        topic=t.topic.name,
        thread_unique_id=t.unique_id,
        slug=t.slug,
        comment_unique_id="this-does-not-exist",
    )
    resp = user.get(url)
    assert resp.status_code == http.HTTPStatus.NOT_FOUND
