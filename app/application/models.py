import flask_login
import flask_migrate
import flask_sqlalchemy
from sqlalchemy_utils import EmailType


db = flask_sqlalchemy.SQLAlchemy()
migrate = flask_migrate.Migrate()


class ApiToken(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"))
    value = db.Column(db.String)


class User(db.Model, flask_login.UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    api_tokens = db.relationship("ApiToken", backref="user", cascade="all, delete")
    deleted = db.Column(db.Boolean, default=False)
    email = db.Column(EmailType, unique=True)
    is_admin = db.Column(db.Boolean, default=False)
    password_hash = db.Column(db.String)
