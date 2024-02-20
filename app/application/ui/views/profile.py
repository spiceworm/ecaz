import operator

import flask
import flask_login

from application.ui import forms


__all__ = (
    "profile",
    "profile_saved",
    "profile_submissions",
    "profile_votes",
)


@flask_login.login_required
def profile() -> flask.Response:
    discussion = flask_login.current_user.discussion
    submissions = sorted(
        discussion.comments + discussion.threads,
        key=operator.attrgetter("created_at"),
        reverse=True,
    )
    return flask.render_template(
        "profile.html",
        create_comment_form=forms.CreateCommentForm(),
        logout_form=forms.LogoutForm(),
        objects=submissions,
    )


@flask_login.login_required
def profile_saved() -> str:
    discussion = flask_login.current_user.discussion
    # TODO: sort these in the order the user saved them and not the order that the object was created
    saves = sorted(
        discussion.saved_comments + discussion.saved_threads,
        key=operator.attrgetter("created_at"),
        reverse=True,
    )
    return flask.render_template(
        "profile.html",
        create_comment_form=forms.CreateCommentForm(),
        logout_form=forms.LogoutForm(),
        objects=saves,
    )


@flask_login.login_required
def profile_submissions() -> str:
    discussion = flask_login.current_user.discussion
    submissions = sorted(
        discussion.comments + discussion.threads,
        key=operator.attrgetter("created_at"),
        reverse=True,
    )
    return flask.render_template(
        "profile.html",
        create_comment_form=forms.CreateCommentForm(),
        logout_form=forms.LogoutForm(),
        objects=submissions,
    )


@flask_login.login_required
def profile_votes() -> str:
    discussion = flask_login.current_user.discussion
    objects = [
        v.submission
        for v in sorted(
            discussion.comment_votes + discussion.thread_votes,
            key=operator.attrgetter("created_at"),
            reverse=True,
        )
    ]
    return flask.render_template(
        "profile.html",
        create_comment_form=forms.CreateCommentForm(),
        logout_form=forms.LogoutForm(),
        objects=objects,
    )
