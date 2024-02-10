import functools

import flask
import flask_login

from application.constants import messages
from application.models import AuthToken


__all__ = (
    "require_moderator",
    "require_unauthenticated",
    "validate_jwt_as_auth_token",
)


def require_moderator(if_not_moderator_redirect_to):
    """
    Decorator used on view functions that should only be accessed if the current user is a moderator
    of at least one topic. If not, redirect them to `if_not_moderator_redirect_to`.
    """

    def decorator(view_func):
        @functools.wraps(view_func)
        def wrapper(*args, **kwargs):
            if not flask_login.current_user.discussion.moderator_of:
                return flask.redirect(flask.url_for(if_not_moderator_redirect_to))
            return view_func(*args, **kwargs)

        return wrapper

    return decorator


def require_unauthenticated(if_authenticated_redirect_to):
    """
    Decorator used on view functions that should only be accessed if the current user is not authenticated.
    If the current user is authenticated, redirect them to `if_authenticated_redirect_to`.
    """

    def decorator(view_func):
        @functools.wraps(view_func)
        def wrapper(*args, **kwargs):
            if flask_login.current_user.is_authenticated:
                return flask.redirect(flask.url_for(if_authenticated_redirect_to))
            return view_func(*args, **kwargs)

        return wrapper

    return decorator


def validate_jwt_as_auth_token(require_tags=(), allow_expired=False, error_redirect=".login"):
    """
    Decorator used on view functions that take a JWT string as an argument. Lookup the `AuthToken` instance
    associated with the JWT. If no `AuthToken` exists, the `AuthToken` is missing any tags specified in
    `require_tags`, or the token is expired and `allow_expired=False`, then redirect to the endpoint
    specified by `error_redirect`.
    """

    def decorator(view_func):
        @functools.wraps(view_func)
        def wrapper(jwt):
            token = AuthToken.query.filter(AuthToken.value == jwt).one_or_none()
            if token and token.validate(require_tags=require_tags, allow_expired=allow_expired):
                return view_func(token)
            else:
                flask.flash(messages.INVALID_TOKEN, category="error")
                return flask.redirect(flask.url_for(error_redirect))

        return wrapper

    return decorator
