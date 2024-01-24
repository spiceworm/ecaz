import os

from flask import (
    Flask,
    g,
)
from flask_bcrypt import Bcrypt
from flask_jwt_extended import JWTManager
from flask_login import LoginManager


def create_app():
    class Config:
        DEBUG = bool(int(os.getenv("DEBUG", "1")))
        PROD = bool(int(os.getenv("PROD", "0")))
        TESTING = bool(int(os.getenv("TESTING", "1")))
        SECRET_KEY = os.environ["SECRET_KEY"]

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

    login_manager = LoginManager()
    login_manager.login_view = "ui_bp.login"
    login_manager.init_app(app)

    from .api import api_bp

    app.register_blueprint(api_bp)

    from .ui import ui_bp

    app.register_blueprint(ui_bp)

    from .models import db, User

    db.init_app(app)

    with app.app_context():
        db.create_all()

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
        return User.query.get(user_id)

    return app
