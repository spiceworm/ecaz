import flask_login
import flask_migrate
import flask_sqlalchemy


db = flask_sqlalchemy.SQLAlchemy()
migrate = flask_migrate.Migrate()


class ApiToken(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"))
    value = db.Column(db.String)


class User(db.Model, flask_login.UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    api_tokens = db.relationship("ApiToken", backref="user")
    is_admin = db.Column(db.Boolean, default=False)
    password_hash = db.Column(db.String)
    username = db.Column(db.String, unique=True)
