import flask
import flask_login

from application.models import Topic
from application.ui import forms
from application.util.decorators import require_moderator


__all__ = (
    "moderation_home",
    "moderation_topic",
)


@flask_login.login_required
@require_moderator(if_not_moderator_redirect_to="ui_bp.profile")
def moderation_home():
    return flask.render_template(
        "discussion/moderation/home.html",
        logout_form=forms.LogoutForm(),
    )


@flask_login.login_required
@require_moderator(if_not_moderator_redirect_to="ui_bp.profile")
def moderation_topic(topic):
    if _topic := Topic.query.filter_by(name=topic).one_or_none():
        if flask_login.current_user.discussion.is_moderator_of(_topic):
            return flask.render_template(
                "discussion/moderation/topic.html",
                topic=_topic,
                logout_form=forms.LogoutForm(),
            )
    return flask.redirect(flask.url_for("ui_bp.profile"))
