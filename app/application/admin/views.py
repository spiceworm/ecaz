import flask
from flask_admin.contrib.sqla import ModelView
import flask_login


class AdminModelView(ModelView):
    def is_accessible(self):
        return flask_login.current_user.is_authenticated and flask_login.current_user.is_admin

    def inaccessible_callback(self, name, **kwargs):
        return flask.redirect(flask.url_for("ui_bp.login", next=flask.request.url))


class ApiTokenModelView(AdminModelView):
    can_create = False
    can_edit = False


class UserModelView(AdminModelView):
    can_create = False
    can_edit = False
    column_exclude_list = ["password"]
