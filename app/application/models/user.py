from __future__ import annotations
from typing import (
    List,
    Union,
)

import flask_login
import humanize
import sqlalchemy as sa
from sqlalchemy.orm import (
    Mapped,
    mapped_column,
    relationship,
)
from sqlalchemy_utils import StringEncryptedType

from application.models import (
    AuthToken,
    db,
    Discussion,
    get_encryption_key,
    MFA,
    utcnow,
)


__all__ = ("User",)


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
    discussion: Mapped[List["Discussion"]] = relationship(
        back_populates="user",
        cascade="all, delete-orphan",
        uselist=False,
    )
    email = sa.Column(
        StringEncryptedType(
            key=get_encryption_key,
            padding="pkcs5",
        ),
        nullable=False,
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
    mfa: Mapped[List["MFA"]] = relationship(
        back_populates="user",
        cascade="all, delete-orphan",
        uselist=False,
    )
    password = sa.Column(
        StringEncryptedType(
            key=get_encryption_key,
            padding="pkcs5",
        ),
        nullable=False,
    )
    username = sa.Column(
        StringEncryptedType(
            key=get_encryption_key,
            padding="pkcs5",
        ),
        nullable=False,
        unique=True,
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        db.session.add_all(
            [
                Discussion(user=self),
                MFA(user=self),
            ]
        )
        db.session.commit()

    @property
    def humanized_created_at(self) -> str:
        return humanize.naturaltime(self.created_at)

    @property
    def frontend_token(self) -> AuthToken:
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

    @staticmethod
    def from_jwt_identity(jwt_identity: str) -> Union[User, None]:
        return User.query.filter_by(id=jwt_identity).one_or_none()

    @property
    def public_auth_tokens(self) -> List[AuthToken]:
        return [t for t in self.auth_tokens if AuthToken.HIDDEN_TAG not in t.tags]
