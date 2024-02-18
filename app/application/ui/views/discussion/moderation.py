from datetime import (
    datetime,
    timedelta,
    timezone,
)

import flask
import flask_login

from application.constants import (
    expires,
    messages,
)
from application.models import (
    Ban,
    Topic,
    User,
)
from application.ui import forms
from application.util.decorators import require_moderator


__all__ = (
    "moderation_home",
    "moderation_topic",
    "moderation_topic_bans",
    "moderation_topic_settings",
    "moderation_topic_subscribe_requests",
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


@flask_login.login_required
@require_moderator(if_not_moderator_redirect_to="ui_bp.profile")
def moderation_topic_bans(topic):
    if _topic := Topic.query.filter_by(name=topic).one_or_none():
        if flask_login.current_user.discussion.is_moderator_of(_topic):
            form = forms.CreateTopicBanForm()
            if form.validate_on_submit():
                expires_unit = form.expires_at_unit.data
                if expires_unit == expires.NEVER:
                    expires_at = None
                else:
                    expires_delta = timedelta(**{expires_unit.lower(): int(form.expires_at_number.data)})
                    expires_at = datetime.now(tz=timezone.utc) + expires_delta

                # We have already validated that `form.username` corresponds to an existing `User`
                banned_user = User.query.filter_by(username=form.username.data).first()

                if Ban.query.filter_by(discussion=banned_user.discussion, topic=_topic).one_or_none():
                    flask.flash(message=messages.BAN_ALREADY_EXISTS_FOR_USER, category="error")
                else:
                    _topic.create_ban(
                        created_by=flask_login.current_user.discussion,
                        discussion=banned_user.discussion,
                        expires_at=expires_at,
                        is_shadow=form.is_shadow.data,
                        reason=form.reason.data,
                    )

            return flask.render_template(
                "discussion/moderation/bans.html",
                create_topic_ban_form=form,
                topic=_topic,
                logout_form=forms.LogoutForm(),
            )
    return flask.redirect(flask.url_for("ui_bp.profile"))


@flask_login.login_required
@require_moderator(if_not_moderator_redirect_to="ui_bp.profile")
def moderation_topic_settings(topic):
    if _topic := Topic.query.filter_by(name=topic).one_or_none():
        if flask_login.current_user.discussion.is_moderator_of(_topic):
            return flask.render_template(
                "discussion/moderation/settings.html",
                topic=_topic,
                logout_form=forms.LogoutForm(),
            )
    return flask.redirect(flask.url_for("ui_bp.profile"))


@flask_login.login_required
@require_moderator(if_not_moderator_redirect_to="ui_bp.profile")
def moderation_topic_subscribe_requests(topic):
    if _topic := Topic.query.filter_by(name=topic).one_or_none():
        if flask_login.current_user.discussion.is_moderator_of(_topic):
            return flask.render_template(
                "discussion/moderation/topic_subscribe_requests.html",
                topic=_topic,
                logout_form=forms.LogoutForm(),
            )
    return flask.redirect(flask.url_for("ui_bp.profile"))
