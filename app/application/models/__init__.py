import flask
import flask_migrate
import flask_sqlalchemy
from sqlalchemy import event


db = flask_sqlalchemy.SQLAlchemy()
migrate = flask_migrate.Migrate()


def get_encryption_key():
    return flask.current_app.config["SECRET_KEY"]


from .auth_token import *
from .totp import *
from .webauthn import *
from .user import *


@event.listens_for(db.session, "loaded_as_persistent")
def receive_loaded_as_persistent(session, instance):
    """Automatically delete expired `AuthToken` entries."""
    if isinstance(instance, AuthToken) and instance.is_expired:
        session.delete(instance)
        session.commit()
