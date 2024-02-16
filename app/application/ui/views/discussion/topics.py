import flask

from application.constants import sort_by
from application.models import Discussion
from application.ui import forms


__all__ = ("view_topics",)


def view_topics() -> str:
    topics_sorting = flask.request.args.get("sorting", sort_by.TOPICS_DEFAULT)
    topics_thread_count = Discussion.get_topics(
        sorting=topics_sorting,
        include_thread_count=True,
    )
    return flask.render_template(
        "discussion/topics/view.html",
        topics_thread_count=topics_thread_count,
        logout_form=forms.LogoutForm(),
        sort_topics_form=forms.SortTopicsForm(sorting=topics_sorting),
    )
