from typing import Union

import flask
import flask_login

from application.models import (
    db,
    Thread,
    Topic,
)
from application.ui import forms


__all__ = (
    "create_thread",
    "view_thread",
)


@flask_login.login_required
def create_thread(topic=None) -> Union[str, flask.Response]:
    topic_choices = [(t.id, t.name) for idx, t in enumerate(Topic.query.order_by(Topic.name))]

    # If the user clicked the link to create a new thread while browsing a specific topic,
    # select that topic as the default value on the topic SelectField dropdown on the create
    # thread form.
    form_kwargs = {}
    if topic:
        topic_ids = {topic_name: topic_id for topic_id, topic_name in topic_choices}
        if requested_topic_id := topic_ids.get(topic):
            form_kwargs["topic_id"] = requested_topic_id

    form = forms.CreateThreadForm(**form_kwargs)
    form.topic_id.choices = topic_choices

    if form.validate_on_submit():
        topic_name = dict(topic_choices)[int(form.topic_id.data)]
        _topic = Topic.query.filter_by(name=topic_name).one_or_none()
        thread = _topic.create_thread(
            body=form.body.data,
            discussion=flask_login.current_user.discussion,
            title=form.title.data,
        )
        return flask.redirect(
            flask.url_for(
                ".view_thread",
                topic=_topic.name,
                thread_unique_id=thread.unique_id,
                slug=thread.slug,
            )
        )
    return flask.render_template(
        "discussion/thread/create.html",
        form=form,
        logout_form=forms.LogoutForm(),
        topic_name=topic,
    )


def view_thread(topic: str, thread_unique_id: str, slug: str) -> str:
    query = Thread.query.filter_by(unique_id=thread_unique_id)
    thread = db.one_or_404(query)
    return flask.render_template(
        "discussion/thread/view.html",
        form=forms.CreateCommentForm(),
        thread=thread,
        logout_form=forms.LogoutForm(),
    )
