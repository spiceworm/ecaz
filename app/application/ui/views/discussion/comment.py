from typing import Union

import flask
import flask_login

from application.models import (
    Comment,
    Thread,
)
from application.ui import forms


__all__ = ("create_comment",)


@flask_login.login_required
def create_comment(topic: str, thread_unique_id: str, slug: str, parent_unique_id: str) -> Union[str, flask.Response]:
    form = forms.CreateCommentForm()
    if form.validate_on_submit():
        thread = Thread.query.filter_by(unique_id=thread_unique_id).one_or_none()

        # `parent_unique_id` will be equal to `Thread.unique_id` if a top level comment is being created.
        # Otherwise a nested comment is being created.
        if thread.unique_id == parent_unique_id:
            parent_obj = thread
        else:
            parent_obj = Comment.query.filter_by(unique_id=parent_unique_id).one_or_none()
        parent_obj.create_comment(
            body=form.body.data,
            discussion=flask_login.current_user.discussion,
        )

    return flask.redirect(
        flask.url_for(
            ".view_thread",
            topic=topic,
            thread_unique_id=thread_unique_id,
            slug=slug,
        ),
    )
