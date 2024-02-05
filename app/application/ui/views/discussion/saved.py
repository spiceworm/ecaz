import flask
import flask_login

from application.ui import forms


__all__ = ("view_saved",)


@flask_login.login_required
def view_saved() -> str:
    discussion = flask_login.current_user.discussion
    objects = sorted(
        [*discussion.saved_comments, *discussion.saved_threads],
        key=lambda obj: obj.created_at,
        reverse=True,
    )
    return flask.render_template(
        "discussion/saved.html",
        create_comment_form=forms.CreateCommentForm(),
        objects=objects,
        logout_form=forms.LogoutForm(),
    )
