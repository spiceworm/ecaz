from datetime import timedelta
import os
from typing import List

import flask_jwt_extended
import flask_login
import flask_migrate
import flask_sqlalchemy
import jwt
import sqlalchemy as sa
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.orm import (
    Mapped,
    mapped_column,
    relationship,
)
from sqlalchemy_utils import StringEncryptedType


db = flask_sqlalchemy.SQLAlchemy()
migrate = flask_migrate.Migrate()


def get_encryption_key():
    return os.environ["SECRET_KEY"]


class ApiToken(db.Model):
    HIDDEN_TAG = "hidden"
    RESET_PASSWORD_TAG = "reset-password"
    VERIFY_EMAIL_TAG = "verify-email"

    id: Mapped[int] = mapped_column(
        primary_key=True,
    )
    name = sa.Column(
        StringEncryptedType(
            key=get_encryption_key,
            padding='pkcs5',
        ),
    )
    user: Mapped["User"] = relationship(
        back_populates="api_tokens",
    )
    user_id: Mapped[int] = mapped_column(
        sa.ForeignKey("user.id"),
    )
    value = sa.Column(
        StringEncryptedType(
            key=get_encryption_key,
            padding='pkcs5',
        ),
    )

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
    id: Mapped[int] = mapped_column(
        primary_key=True,
    )
    api_tokens: Mapped[List["ApiToken"]] = relationship(
        back_populates="user",
        cascade="all, delete-orphan",
    )
    deleted = sa.Column(
        StringEncryptedType(
            type_in=sa.Boolean,
            key=get_encryption_key,
            padding='zeroes',
        ),
        default=False,
    )
    email = sa.Column(
        StringEncryptedType(
            key=get_encryption_key,
            padding='pkcs5',
        ),
        unique=True,
    )
    is_admin = sa.Column(
        StringEncryptedType(
            type_in=sa.Boolean,
            key=get_encryption_key,
            padding='zeroes',
        ),
        default=False,
    )
    password = sa.Column(
        StringEncryptedType(
            key=get_encryption_key,
            padding='pkcs5',
        ),
    )
    verified = sa.Column(
        StringEncryptedType(
            type_in=sa.Boolean,
            key=get_encryption_key,
            padding='zeroes',
        ),
        default=False,
    )

    @hybrid_property
    def public_api_tokens(self):
        return [t for t in self.api_tokens if "hidden" not in t.tags]
