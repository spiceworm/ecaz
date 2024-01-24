import flask
import flask_migrate
import flask_sqlalchemy
import sqlalchemy as sa
from sqlalchemy.ext.compiler import compiles


db = flask_sqlalchemy.SQLAlchemy()
migrate = flask_migrate.Migrate()


def get_encryption_key():
    return flask.current_app.config["SECRET_KEY"]


class utcnow(sa.sql.expression.FunctionElement):
    type = sa.DateTime()
    inherit_cache = True


@compiles(utcnow, "postgresql")
def pg_utcnow(element, compiler, **kw) -> str:
    return "TIMEZONE('utc', CURRENT_TIMESTAMP)"


from .auth_token import *
from .discussion import *
from .totp import *
from .webauthn import *
from .user import *


@sa.event.listens_for(db.session, "loaded_as_persistent")
def receive_loaded_as_persistent(session, instance):
    """Automatically delete expired `AuthToken` entries."""
    if isinstance(instance, AuthToken) and instance.is_expired:
        session.delete(instance)
        session.commit()
