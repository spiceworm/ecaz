from logging.config import dictConfig
import os
import sqlite3

from flask import (
    Flask,
    g,
)
from flask_login import LoginManager


class Config:
    DB_PATH = os.environ["DB_PATH"]
    DEBUG = bool(int(os.getenv("DEBUG", "0")))
    PROD = bool(int(os.getenv("PROD", "0")))
    TESTING = bool(int(os.getenv("TESTING", "0")))
    SECRET_KEY = os.environ["SECRET_KEY"]
    SQLALCHEMY_DATABASE_URI = f"sqlite:///{DB_PATH}"

    def json(self):
        return {
            attr: getattr(self, attr)
            for attr in (
                "DB_PATH",
                "DEBUG",
                "PROD",
                "TESTING",
                "SQLALCHEMY_DATABASE_URI",
            )
        }


config = Config()


dictConfig(
    {
        "version": 1,
        "formatters": {
            "default": {
                "format": "[%(asctime)s] %(levelname)s in %(module)s: %(message)s",
            }
        },
        "handlers": {
            "wsgi": {
                "class": "logging.StreamHandler",
                "stream": "ext://flask.logging.wsgi_errors_stream",
                "formatter": "default",
            }
        },
        "root": {"level": "INFO" if config.PROD else "DEBUG", "handlers": ["wsgi"]},
    }
)


def create_app():
    app = Flask(
        __name__,
        static_folder=None,
        template_folder=None,
    )

    with app.app_context():
        g.config = config

    app.config.from_object(config)
    app.logger.debug(config.json())

    login_manager = LoginManager()
    login_manager.init_app(app)

    from .api import api_bp

    app.register_blueprint(api_bp)

    from .ui import ui_bp

    app.register_blueprint(ui_bp)

    from .models import db, User

    db.init_app(app)

    @login_manager.user_loader
    def load_user(user_id):
        """ Callback function that tells flask-login how to reload
        an object for a user that has already been authenticated,
        such as when someone reconnects to a "remember me" session """
        return User.query.get(user_id)

    with app.app_context():
        db.create_all()

    return app
