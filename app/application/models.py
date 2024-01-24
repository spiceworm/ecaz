import flask_login
import flask_sqlalchemy


db = flask_sqlalchemy.SQLAlchemy()


class ApiToken(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.Unicode)
    value = db.Column(db.Unicode)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"))


class User(db.Model, flask_login.UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.Unicode)
    password = db.Column(db.Unicode)
    api_tokens = db.relationship("ApiToken", backref="user")
