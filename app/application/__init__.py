import os

import flask
from flask import (
    Flask,
    g,
)
import flask_admin
from flask_admin.contrib.sqla import ModelView
import flask_jwt_extended
import flask_login
import flask_mailman


class AdminModelView(ModelView):
    def is_accessible(self):
        return flask_login.current_user.is_authenticated and flask_login.current_user.is_admin

    def inaccessible_callback(self, name, **kwargs):
        return flask.redirect(flask.url_for("ui_bp.login", next=flask.request.url))


def create_app():
    from .api import api_bp
    from .ui import ui_bp
    from .models import (
        ApiToken,
        db,
        migrate,
        User,
    )

    class Config:
        BASE_URL = os.environ["BASE_URL"]

        DEBUG = bool(int(os.getenv("DEBUG", "1")))
        FLASK_ADMIN_SWATCH = os.getenv("FLASK_ADMIN_SWATCH", "cerulean")
        PROD = bool(int(os.getenv("PROD", "0")))
        SECRET_KEY = os.environ["SECRET_KEY"]
        TESTING = bool(int(os.getenv("TESTING", "1")))
        WTF_CSRF_ENABLED = bool(int(os.getenv("WTF_CSRF_ENABLED", "1")))

        MAIL_DEFAULT_SENDER = os.environ["MAIL_DEFAULT_SENDER"]
        MAIL_PASSWORD = os.environ["MAIL_PASSWORD"]
        MAIL_PORT = int(os.getenv("MAIL_PORT", 587))
        MAIL_SERVER = os.environ["MAIL_SERVER"]
        MAIL_TIMEOUT = int(os.getenv("MAIL_TIMEOUT", 10))
        MAIL_USE_TLS = MAIL_PORT == 587
        MAIL_USE_SSL = MAIL_PORT == 465
        MAIL_USERNAME = os.environ["MAIL_USERNAME"]

        POSTGRES_DB = os.environ["POSTGRES_DB"]
        POSTGRES_HOST = os.environ["POSTGRES_HOST"]
        POSTGRES_PASSWORD = os.environ["POSTGRES_PASSWORD"]
        POSTGRES_PORT = os.environ["POSTGRES_PORT"]
        POSTGRES_SSL = bool(int(os.getenv("POSTGRES_SSL", "1")))
        POSTGRES_USER = os.environ["POSTGRES_USER"]

        # Magic flask-sqlalchemy environment variable
        SQLALCHEMY_DATABASE_URI = (
            f"postgresql://{POSTGRES_USER}:{POSTGRES_PASSWORD}"
            f"@{POSTGRES_HOST}:{POSTGRES_PORT}/{POSTGRES_DB}"
        ) + ("?sslmode=require" if POSTGRES_SSL else "")

        # Magic flask-sqlalchemy environment variable
        SQLALCHEMY_ENGINE_OPTIONS = {
            # Each time the connection is used, send a SELECT 1 query to check the connection.
            # If it fails, then the connection is recycled and checked again.
            # Upon success, the query is then executed.
            "pool_pre_ping": True,
        }

        def json(self):
            return {attr: getattr(self, attr) for attr in dir(self) if attr.isupper()}

    app = Flask(
        __name__,
        static_folder=None,
        template_folder=None,
    )
    app.register_blueprint(api_bp)
    app.register_blueprint(ui_bp)

    config = Config()
    app.config.from_object(config)
    app.logger.debug(config.json())

    flask_jwt_extended.JWTManager(app)
    flask_mailman.Mail(app)

    login_manager = flask_login.LoginManager()
    login_manager.login_view = "ui_bp.login"
    login_manager.init_app(app)

    db.init_app(app)
    migrate.init_app(app, db)
    with app.app_context():
        db.create_all()

    admin = flask_admin.Admin(app, name="ecaz_xyz", template_mode="bootstrap3")
    admin.add_view(AdminModelView(ApiToken, db.session))
    admin.add_view(AdminModelView(User, db.session))

    @app.before_request
    def define_globals():
        """No custom attributes will be available on `flask.g` unless
        they are set on the `flask.g` object here."""
        g.config = config

    @login_manager.user_loader
    def load_user(user_id):
        """Callback function that tells flask-login how to reload
        an object for a user that has already been authenticated,
        such as when someone reconnects to a "remember me" session"""
        return db.session.get(User, user_id)

    return app
