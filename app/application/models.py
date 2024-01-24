import flask_login
import flask_sqlalchemy


db = flask_sqlalchemy.SQLAlchemy()


class ApiToken(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    value = db.Column(db.String)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"))


class User(db.Model, flask_login.UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String)
    password_hash = db.Column(db.String)
    api_tokens = db.relationship("ApiToken", backref="user")
