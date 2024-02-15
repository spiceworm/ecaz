import flask
import sqlalchemy as sa
from sqlalchemy.orm import load_only

from application.models import (
    db,
    Thread,
    Topic,
)
from application.ui import forms


__all__ = ("view_topics",)


def view_topics() -> str:
    thread_count = sa.func.count(Topic.threads)

    query = (
        db.session.query(Topic, thread_count)
        .outerjoin(Thread)
        .group_by(Topic.id)
        .order_by(thread_count.desc())
        .options(
            load_only(
                Topic.description,
                Topic.is_private,
                Topic.name,
            )
        )
    )

    return flask.render_template(
        "discussion/topics/view.html",
        query=query,
        logout_form=forms.LogoutForm(),
    )
