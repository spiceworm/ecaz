import flask
import flask_migrate
import flask_sqlalchemy


db = flask_sqlalchemy.SQLAlchemy()
migrate = flask_migrate.Migrate()


def get_encryption_key():
    return flask.current_app.config["SECRET_KEY"]


from .api_token import *
from .totp import *
from .user import *
