from typing import List

import flask_login
import sqlalchemy as sa
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.orm import (
    Mapped,
    mapped_column,
    relationship,
)
from sqlalchemy_utils import StringEncryptedType

from . import (
    db,
    get_encryption_key,
)


__all__ = ("User",)


def default_username(ctx):
    """Make `User.username` default to the value of `User.email`"""
    return ctx.get_current_parameters()["email"]


class User(db.Model, flask_login.UserMixin):
    id: Mapped[int] = mapped_column(
        nullable=False,
        primary_key=True,
    )
    api_tokens: Mapped[List["ApiToken"]] = relationship(
        back_populates="user",
        cascade="all, delete-orphan",
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
    username = sa.Column(
        StringEncryptedType(
            key=get_encryption_key,
            padding="pkcs5",
        ),
        default=default_username,
        nullable=False,
        unique=True,
    )

    @hybrid_property
    def public_api_tokens(self):
        return [t for t in self.api_tokens if "hidden" not in t.tags]
