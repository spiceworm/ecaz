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
    query = Topic.query.filter_by(name=topic)
    return flask.render_template(
        "discussion/topic/view.html",
        topic=db.one_or_404(query),
        logout_form=forms.LogoutForm(),
    )
