from typing import Union

import flask
import flask_login

from application.constants import messages
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
        user = flask_login.current_user
        topic_name = dict(topic_choices)[int(form.topic_id.data)]
        _topic = Topic.query.filter_by(name=topic_name).one_or_none()

        ban = user.discussion.get_ban_for(_topic)
        if ban and not ban.is_shadow:
            msg = f"{messages.BANNED_FROM_CONTRIBUTING} to {topic_name}. Expires {ban.humanized_expires_at}."
            flask.flash(message=msg, category="info")
        else:
            thread = _topic.create_thread(
                body=form.body.data,
                discussion=user.discussion,
                is_hidden=user.discussion.is_shadow_banned_from(_topic),
                title=form.title.data,
            )
            return flask.redirect(
                flask.url_for(
                    "ui_bp.view_thread",
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
    thread = db.one_or_404(Thread.query.filter_by(unique_id=thread_unique_id))
    return flask.render_template(
        "discussion/thread/view.html",
        create_comment_form=forms.CreateCommentForm(),
        thread=thread,
        logout_form=forms.LogoutForm(),
    )
