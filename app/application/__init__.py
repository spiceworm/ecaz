from logging.config import dictConfig
import os

from flask import Flask
from flask_login import LoginManager


class Config:
    DEBUG = bool(int(os.getenv('DEBUG', '0')))
    PROD = bool(int(os.getenv('PROD', '0')))
    TESTING = bool(int(os.getenv('TESTING', '0')))
    SECRET_KEY = os.environ["SECRET_KEY"]

    def __str__(self):
        return f'{self.DEBUG=}, {self.PROD=}, {self.TESTING=}'


config = Config()

dictConfig({
    'version': 1,
    'formatters': {'default': {
        'format': '[%(asctime)s] %(levelname)s in %(module)s: %(message)s',
    }},
    'handlers': {'wsgi': {
        'class': 'logging.StreamHandler',
        'stream': 'ext://flask.logging.wsgi_errors_stream',
        'formatter': 'default'
    }},
    'root': {
        'level': 'INFO' if config.PROD else 'DEBUG',
        'handlers': ['wsgi']
    }
})


def create_app():
    app = Flask(
        __name__,
        static_folder=None,
        template_folder=None,
    )

    app.config.from_object(config)
    app.logger.debug(config)

    login_manager = LoginManager()
    login_manager.init_app(app)

    @login_manager.user_loader
    def load_user(user_id):
        pass
        # return User.get(user_id)

    from .api import api_bp

    app.register_blueprint(api_bp)

    from .ui import ui_bp

    app.register_blueprint(ui_bp)

    return app
