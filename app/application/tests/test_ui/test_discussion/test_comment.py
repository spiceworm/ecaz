import http

import flask
from flask import url_for

from application.constants import messages
from application.models import Comment


class TestCreateComment:
    endpoint = "ui_bp.create_comment"

    def test_create_if_banned(self, topic, ui_user):
        user1 = ui_user()
        user2 = ui_user()
        _topic = topic(moderators=[user1.discussion])
        _topic.create_ban(created_by=user1.discussion, discussion=user2.discussion, reason="testing")
        t = _topic.create_thread(title="t", body="b", discussion=user1.discussion)
        resp = user2.post(
            url_for(
                self.endpoint,
                topic=t.topic.name,
                thread_unique_id=t.unique_id,
                slug=t.slug,
                parent_unique_id=t.unique_id,
            ),
            data={"body": "comment"},
            follow_redirects=True,
        )
        assert messages.BANNED_FROM_CONTRIBUTING in resp.data.decode()
        assert resp.request.base_url == url_for(
            "ui_bp.view_thread",
            topic=t.topic.name,
            thread_unique_id=t.unique_id,
            slug=t.slug,
        )

    def test_create_if_shadow_banned(self, topic, ui_user):
        user1 = ui_user()
        user2 = ui_user()
        _topic = topic(moderators=[user1.discussion])
        _topic.create_ban(created_by=user1.discussion, discussion=user2.discussion, reason="testing", is_shadow=True)
        t = _topic.create_thread(body="b", title="t", discussion=user1.discussion)
        resp = user2.post(
            url_for(
                self.endpoint,
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

    def test_create_if_thread_is_locked(self, thread, ui_user):
        user = ui_user()
        t = thread(body="b", title="t", discussion=user.discussion, is_locked=True)
        body = "this is the body of the comment i want to post to the locked thread"
        resp = user.post(
            url_for(
                self.endpoint,
                topic=t.topic.name,
                thread_unique_id=t.unique_id,
                slug=t.slug,
                parent_unique_id=t.unique_id,
            ),
            data={"body": "comment"},
            follow_redirects=True,
        )
        assert messages.THREAD_IS_LOCKED in resp.data.decode()
        assert Comment.query.filter_by(body=body).one_or_none() is None

    def test_nested_comment(self, comment, ui_user):
        user = ui_user()
        d = user.discussion
        parent_comment = comment(discussion=d)
        child_comment_body = "this the child comment"
        resp = user.post(
            url_for(
                self.endpoint,
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

    def test_top_level_comment(self, thread, ui_user):
        user = ui_user()
        t = thread(body="b", title="t", discussion=user.discussion)
        resp = user.post(
            url_for(
                self.endpoint,
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


class TestViewComment:
    endpoint = "ui_bp.view_comment"

    def test_view_permalinked_comment(self, comment, ui_user):
        user = ui_user()
        c = comment(discussion=user.discussion)
        url = flask.url_for(
            self.endpoint,
            topic=c.thread.topic.name,
            thread_unique_id=c.thread.unique_id,
            slug=c.thread.slug,
            comment_unique_id=c.unique_id,
        )
        resp = user.get(url)
        assert resp.request.base_url == url

    def test_view_permalinked_comment_that_does_not_exist(self, thread, ui_user):
        user = ui_user()
        t = thread(discussion=user.discussion)
        url = flask.url_for(
            self.endpoint,
            topic=t.topic.name,
            thread_unique_id=t.unique_id,
            slug=t.slug,
            comment_unique_id="this-does-not-exist",
        )
        resp = user.get(url)
        assert resp.status_code == http.HTTPStatus.NOT_FOUND

    def test_view_permalinked_comment_as_creator_of_hidden_comment(self, comment, ui_user):
        u = ui_user()
        c = comment(body="unique text for the comment body", discussion=u.discussion, is_hidden=True)
        url = url_for(
            self.endpoint,
            topic=c.thread.topic.name,
            thread_unique_id=c.thread.unique_id,
            slug=c.thread.slug,
            comment_unique_id=c.unique_id,
        )
        resp = u.get(url)
        assert c.body in resp.data.decode()

    def test_view_permalinked_comment_as_authenticated_noncreator_of_hidden_comment(self, comment, ui_user):
        u1 = ui_user()
        u2 = ui_user()
        c = comment(body="unique text for the comment body", discussion=u1.discussion, is_hidden=True)
        url = url_for(
            self.endpoint,
            topic=c.thread.topic.name,
            thread_unique_id=c.thread.unique_id,
            slug=c.thread.slug,
            comment_unique_id=c.unique_id,
        )
        resp = u2.get(url)
        assert c.body not in resp.data.decode()

    def test_view_permalinked_comment_as_unauthenticated_noncreator_of_hidden_comment(self, client, comment, user):
        u = user()
        c = comment(body="unique text for the comment body", discussion=u.discussion, is_hidden=True)
        url = url_for(
            self.endpoint,
            topic=c.thread.topic.name,
            thread_unique_id=c.thread.unique_id,
            slug=c.thread.slug,
            comment_unique_id=c.unique_id,
        )
        resp = client.get(url)
        assert c.body not in resp.data.decode()
