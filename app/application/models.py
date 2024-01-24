import flask_login
import flask_sqlalchemy
import flask_wtf
import wtforms


db = flask_sqlalchemy.SQLAlchemy()


class User(db.Model, flask_login.UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.Unicode)
    password = db.Column(db.Unicode)


class LoginForm(flask_wtf.Form):
    username = wtforms.StringField("username")
    password = wtforms.PasswordField("password")
