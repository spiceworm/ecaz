import os

import flask_migrate
import flask_sqlalchemy


db = flask_sqlalchemy.SQLAlchemy()
migrate = flask_migrate.Migrate()


def get_encryption_key():
    return os.environ["SECRET_KEY"]


from .api_token import *
from .user import *
