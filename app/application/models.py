import flask_login
import flask_sqlalchemy
import flask_wtf
import wtforms


db = flask_sqlalchemy.SQLAlchemy()


class ApiToken(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    token = db.Column(db.Unicode)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"))


# TODO: move this to a separate forms.py file
class LoginForm(flask_wtf.Form):
    username = wtforms.StringField("username")
    password = wtforms.PasswordField("password")


class User(db.Model, flask_login.UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.Unicode)
    password = db.Column(db.Unicode)
    api_tokens = db.relationship("ApiToken", backref="user")
