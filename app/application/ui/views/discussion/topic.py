from typing import Union

import flask
import flask_login

from application.constants import messages
from application.models import (
    db,
    Topic,
)
from application.ui import forms


__all__ = (
    "create_topic",
    "view_topic",
)


@flask_login.login_required
def create_topic() -> Union[str, flask.Response]:
    form = forms.CreateTopicForm()
    if form.validate_on_submit():
        if not Topic.query.filter_by(name=form.name.data).one_or_none():
            user = flask_login.current_user
            topic = Topic(
                name=form.name.data,
                description=form.description.data,
                is_private=form.is_private.data,
                moderators=[user.discussion],
            )
            user.discussion.add_subscription(topic)
            db.session.add_all([topic, user])
            db.session.commit()
            return flask.redirect(flask.url_for(".view_topic", topic=topic.name))
        else:
            flask.flash(messages.TOPIC_ALREADY_EXISTS, category="error")

    return flask.render_template(
        "discussion/topic/create.html",
        form=form,
        logout_form=forms.LogoutForm(),
    )


def view_topic(topic: str) -> str:
    topic = db.one_or_404(Topic.query.filter_by(name=topic))
    user = flask_login.current_user
    template = "view.html"
    if topic.is_private:
        template = "is_private.html"

        # Make sure the user is authenticated before accessing attributes that will only be
        # present for an authenticated user.
        if user.is_authenticated:
            if user.discussion.is_subscribed_to(topic) or user.discussion.is_moderator_of(topic):
                template = "view.html"

    return flask.render_template(
        f"discussion/topic/{template}",
        topic=topic,
        logout_form=forms.LogoutForm(),
    )
