import flask_jwt_extended
import flask_login
import flask_migrate
import flask_sqlalchemy
import jwt
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy_utils import EmailType


db = flask_sqlalchemy.SQLAlchemy()
migrate = flask_migrate.Migrate()


class ApiToken(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"))
    value = db.Column(db.String)

    @hybrid_property
    def is_expired(self):
        try:
            flask_jwt_extended.decode_token(self.value)
        except jwt.ExpiredSignatureError:
            return True
        return False


class User(db.Model, flask_login.UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    api_tokens = db.relationship("ApiToken", backref="user", cascade="all, delete")
    deleted = db.Column(db.Boolean, default=False)
    email = db.Column(EmailType, unique=True)
    is_admin = db.Column(db.Boolean, default=False)
    password_hash = db.Column(db.String)
    verified = db.Column(db.Boolean, default=False)

    @hybrid_property
    def public_api_tokens(self):
        tokens = []
        for token in self.api_tokens:
            try:
                claims = flask_jwt_extended.decode_token(token.value)
            except jwt.ExpiredSignatureError:
                pass
            else:
                if "hidden" not in claims.get("tags", []):
                    tokens.append(token)
        return tokens
