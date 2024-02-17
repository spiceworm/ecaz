from typing import Union

import flask
import flask_admin
from flask_admin.contrib.sqla import ModelView
import flask_login
from werkzeug.wrappers import Response


class RestrictedIndexView(flask_admin.AdminIndexView):
    @flask_admin.expose("/")
    def index(self) -> Union[str, Response]:
        """
        If any user attempts to access /admin when they are not authenticated as an admin
        User, redirect them to the login page.
        """
        if flask_login.current_user.is_authenticated and flask_login.current_user.is_admin:
            return super().index()
        return flask.redirect(flask.url_for("ui_bp.login"))


class AuthTokenModelView(ModelView):
    can_create = False
    can_edit = False


class BanModelView(ModelView):
    can_view_details = True


class CommentModelView(ModelView):
    can_view_details = True


class DiscussionModelView(ModelView):
    can_view_details = True


class ThreadModelView(ModelView):
    can_view_details = True


class TopicModelView(ModelView):
    can_view_details = True


class TopicSubscribeRequest(ModelView):
    can_view_details = True


class UserModelView(ModelView):
    can_create = False
    can_edit = False
    column_exclude_list = ["password"]
