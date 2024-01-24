import os

import flask
from flask import (
    Flask,
    g,
)
from flask_admin import Admin
from flask_admin.contrib.sqla import ModelView
from flask_bcrypt import Bcrypt
from flask_jwt_extended import JWTManager
import flask_login


class AdminModelView(ModelView):
    def is_accessible(self):
        return flask_login.current_user.is_authenticated and flask_login.current_user.is_admin

    def inaccessible_callback(self, name, **kwargs):
        return flask.redirect(flask.url_for("ui_bp.login", next=flask.request.url))


def create_app():
    class Config:
        DEBUG = bool(int(os.getenv("DEBUG", "1")))
        PROD = bool(int(os.getenv("PROD", "0")))
        TESTING = bool(int(os.getenv("TESTING", "1")))
        SECRET_KEY = os.environ["SECRET_KEY"]
        FLASK_ADMIN_SWATCH = os.getenv("FLASK_ADMIN_SWATCH", "cerulean")
        WTF_CSRF_ENABLED = bool(int(os.getenv("WTF_CSRF_ENABLED", "1")))

        POSTGRES_DB = os.environ["POSTGRES_DB"]
        POSTGRES_HOST = os.environ["POSTGRES_HOST"]
        POSTGRES_PASSWORD = os.environ["POSTGRES_PASSWORD"]
        POSTGRES_PORT = os.environ["POSTGRES_PORT"]
        POSTGRES_SSL = bool(int(os.getenv("POSTGRES_SSL", "1")))
        POSTGRES_USER = os.environ["POSTGRES_USER"]

        # Magic environment variable looked for by sqlalchemy
        SQLALCHEMY_DATABASE_URI = (
            f"postgresql://{POSTGRES_USER}:{POSTGRES_PASSWORD}"
            f"@{POSTGRES_HOST}:{POSTGRES_PORT}/{POSTGRES_DB}"
        ) + ("?sslmode=require" if POSTGRES_SSL else "")

        def json(self):
            return {
                attr: getattr(self, attr)
                for attr in (
                    "DEBUG",
                    "PROD",
                    "TESTING",
                    "SECRET_KEY",
                    "FLASK_ADMIN_SWATCH",
                    "WTF_CSRF_ENABLED",
                    "POSTGRES_DB",
                    "POSTGRES_HOST",
                    "POSTGRES_PASSWORD",
                    "POSTGRES_PORT",
                    "POSTGRES_SSL",
                    "POSTGRES_USER",
                    "SQLALCHEMY_DATABASE_URI",
                )
            }

    app = Flask(
        __name__,
        static_folder=None,
        template_folder=None,
    )

    config = Config()
    app.config.from_object(config)
    app.logger.debug(config.json())

    bcrypt = Bcrypt(app)
    jwt = JWTManager(app)

    login_manager = flask_login.LoginManager()
    login_manager.login_view = "ui_bp.login"
    login_manager.init_app(app)

    from .api import api_bp
    from .ui import ui_bp
    from .models import (
        ApiToken,
        db,
        migrate,
        User,
    )

    app.register_blueprint(api_bp)
    app.register_blueprint(ui_bp)

    db.init_app(app)
    migrate.init_app(app, db)

    with app.app_context():
        db.create_all()

    admin = Admin(app, name="ecaz_xyz", template_mode="bootstrap3")
    admin.add_view(AdminModelView(ApiToken, db.session))
    admin.add_view(AdminModelView(User, db.session))

    @app.before_request
    def define_globals():
        """No custom attributes will be available on `flask.g` unless
        they are set on the `flask.g` object here."""
        g.config = config
        g.bcrypt = bcrypt

    @login_manager.user_loader
    def load_user(user_id):
        """Callback function that tells flask-login how to reload
        an object for a user that has already been authenticated,
        such as when someone reconnects to a "remember me" session"""
        return db.session.get(User, user_id)

    return app
