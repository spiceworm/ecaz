from datetime import timedelta

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
    HIDDEN_TAG = "hidden"
    RESET_PASSWORD_TAG = "reset-password"
    VERIFY_EMAIL_TAG = "verify-email"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"))
    value = db.Column(db.String)

    @classmethod
    def _create_token(cls, user, name, tags=None, expires_delta=None):
        token_value = flask_jwt_extended.create_access_token(
            additional_claims={"tags": tags or []},
            expires_delta=expires_delta,
            identity=user.email,
        )
        return cls(
            name=name,
            value=token_value,
            user=user,
        )

    @classmethod
    def create_email_verification_token(cls, user):
        token = cls._create_token(
            user,
            cls.VERIFY_EMAIL_TAG,
            [cls.HIDDEN_TAG, cls.VERIFY_EMAIL_TAG],
            timedelta(hours=24),
        )
        db.session.add(token)
        db.session.commit()
        return token

    @classmethod
    def create_reset_password_token(cls, user):
        token = cls._create_token(
            user,
            cls.RESET_PASSWORD_TAG,
            [cls.HIDDEN_TAG, cls.RESET_PASSWORD_TAG],
            timedelta(hours=24),
        )
        db.session.add(token)
        db.session.commit()
        return token

    @hybrid_property
    def is_expired(self):
        try:
            flask_jwt_extended.decode_token(self.value)
        except jwt.ExpiredSignatureError:
            return True
        return False

    @hybrid_property
    def tags(self):
        try:
            claims = flask_jwt_extended.decode_token(self.value)
        except jwt.ExpiredSignatureError:
            return []
        else:
            return claims.get("tags", [])


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
        return [t for t in self.api_tokens if "hidden" not in t.tags]
