import flask
import flask_marshmallow
import flask_migrate
import flask_sqlalchemy
import sqlalchemy as sa
from sqlalchemy.ext.compiler import compiles


db = flask_sqlalchemy.SQLAlchemy()
marshmallow = flask_marshmallow.Marshmallow()
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
from .mfa import *
from .user import *
from .schema import *
