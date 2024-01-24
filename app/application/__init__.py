import os

from flask import Flask
from flask_login import LoginManager

from . import config


def create_app():
    app = Flask(
        __name__,
        static_folder=None,
        template_folder=None,
    )

    if "PROD" in os.environ:
        app.config.from_object(config.Production())
    elif "TEST" in os.environ:
        app.config.from_object(config.Testing())
    else:
        app.config.from_object(config.Development())

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
