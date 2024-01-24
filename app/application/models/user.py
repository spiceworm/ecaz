from typing import List

import flask_login
import sqlalchemy as sa
from sqlalchemy.ext.compiler import compiles
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.orm import (
    Mapped,
    mapped_column,
    relationship,
)
from sqlalchemy_utils import StringEncryptedType

from application.models import (
    AuthToken,
    db,
    get_encryption_key,
    Totp,
    WebAuthn,
)


__all__ = ("User",)


class utcnow(sa.sql.expression.FunctionElement):
    type = sa.DateTime()
    inherit_cache = True


@compiles(utcnow, 'postgresql')
def pg_utcnow(element, compiler, **kw):
    return "TIMEZONE('utc', CURRENT_TIMESTAMP)"


def default_username(ctx):
    """Make `User.username` default to the value of `User.email`"""
    return ctx.get_current_parameters()["email"]


class User(db.Model, flask_login.UserMixin):
    id: Mapped[int] = mapped_column(
        nullable=False,
        primary_key=True,
    )
    auth_tokens: Mapped[List["AuthToken"]] = relationship(
        back_populates="user",
        cascade="all, delete-orphan",
    )
    created_at = db.Column(
        db.DateTime(timezone=True),
        nullable=False,
        default=utcnow(),
    )
    email = sa.Column(
        StringEncryptedType(
            key=get_encryption_key,
            padding="pkcs5",
        ),
        nullable=False,
        unique=True,
    )
    is_admin = sa.Column(
        StringEncryptedType(
            type_in=sa.Boolean,
            key=get_encryption_key,
            padding="zeroes",
        ),
        default=False,
    )
    is_banned = sa.Column(
        StringEncryptedType(
            type_in=sa.Boolean,
            key=get_encryption_key,
            padding="zeroes",
        ),
        default=False,
    )
    is_deleted = sa.Column(
        StringEncryptedType(
            type_in=sa.Boolean,
            key=get_encryption_key,
            padding="zeroes",
        ),
        default=False,
    )
    is_verified = sa.Column(
        StringEncryptedType(
            type_in=sa.Boolean,
            key=get_encryption_key,
            padding="zeroes",
        ),
        default=False,
    )
    password = sa.Column(
        StringEncryptedType(
            key=get_encryption_key,
            padding="pkcs5",
        ),
        nullable=False,
    )
    totp: Mapped[List["Totp"]] = relationship(
        back_populates="user",
        cascade="all, delete-orphan",
        uselist=False,
    )
    username = sa.Column(
        StringEncryptedType(
            key=get_encryption_key,
            padding="pkcs5",
        ),
        default=default_username,
        nullable=False,
        unique=True,
    )
    webauthn: Mapped[List["WebAuthn"]] = relationship(
        back_populates="user",
        cascade="all, delete-orphan",
        uselist=False,
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        db.session.add_all([
            Totp(user=self),
            WebAuthn(user=self),
        ])
        db.session.commit()

    @hybrid_property
    def frontend_token(self):
        """
        Returns an `AuthToken` used by the frontend to communicate with the API.
        Returns a new `AuthToken` instance each time the property is accessed.
        """
        for token in self.auth_tokens:
            if AuthToken.FRONTEND_TAG in token.tags:
                db.session.delete(token)
        else:
            db.session.commit()
        return AuthToken.create_frontend_token(self)

    @hybrid_property
    def public_auth_tokens(self):
        return [t for t in self.auth_tokens if AuthToken.HIDDEN_TAG not in t.tags]
