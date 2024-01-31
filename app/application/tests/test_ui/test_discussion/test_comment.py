from flask import url_for

from application.models import Comment


def test_create_top_level_comment(topic, ui_user):
    user = ui_user()
    _topic = topic()
    thread = _topic.create_thread(body="b", title="t", discussion=user.discussion)
    resp = user.post(
        url_for(
            "ui_bp.create_comment",
            topic=_topic.name,
            thread_unique_id=thread.unique_id,
            slug=thread.slug,
            parent_unique_id=thread.unique_id,
        ),
        data={"body": "comment"},
        follow_redirects=True,
    )
    assert len(resp.history) == 1
    assert resp.request.base_url == url_for(
        "ui_bp.view_thread",
        topic=_topic.name,
        thread_unique_id=thread.unique_id,
        slug=thread.slug,
    )


def test_create_nested_comment(topic, ui_user):
    user = ui_user()
    d = user.discussion
    _topic = topic()
    thread = _topic.create_thread(body="b", title="t", discussion=d)
    parent_comment = thread.create_comment(body="b", discussion=d)
    child_comment_body = "this the child comment"
    resp = user.post(
        url_for(
            "ui_bp.create_comment",
            topic=_topic.name,
            thread_unique_id=thread.unique_id,
            slug=thread.slug,
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
        topic=_topic.name,
        thread_unique_id=thread.unique_id,
        slug=thread.slug,
    )
