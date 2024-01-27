import flask

from application.models import Topic
from application.ui import forms


__all__ = ("view_topics",)


def view_topics() -> str:
    return flask.render_template(
        "discussion/topics/view.html",
        topics=Topic.query.order_by(Topic.name),
        logout_form=forms.LogoutForm(),
    )
