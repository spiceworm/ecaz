from __future__ import annotations
from datetime import timedelta
import time
from typing import (
    List,
    Union,
)

import flask_jwt_extended
import humanize
import jwt
import sqlalchemy as sa
from sqlalchemy.orm import (
    Mapped,
    mapped_column,
    relationship,
)
from sqlalchemy_utils import StringEncryptedType

from application.models import (
    db,
    get_encryption_key,
)


__all__ = ("AuthToken",)


class AuthToken(db.Model):
    FRONTEND_TAG = "frontend"
    HIDDEN_TAG = "hidden"
    RESET_PASSWORD_TAG = "reset-password"
    TOTP_MFA_TAG = "mfa/totp"
    VERIFY_EMAIL_TAG = "verify-email"
    WEBAUTHN_MFA_TAG = "mfa/webauthn"

    id: Mapped[int] = mapped_column(
        nullable=False,
        primary_key=True,
    )
    name = sa.Column(
        StringEncryptedType(
            key=get_encryption_key,
            padding="pkcs5",
        ),
        nullable=False,
    )
    user: Mapped["User"] = relationship(
        back_populates="auth_tokens",
    )
    user_id: Mapped[int] = mapped_column(
        sa.ForeignKey("user.id"),
        nullable=False,
    )
    value = sa.Column(
        StringEncryptedType(
            key=get_encryption_key,
            padding="pkcs5",
        ),
        nullable=False,
    )

    @classmethod
    def create(cls, user, name, tags=None, expires_delta=False) -> AuthToken:
        token_value = flask_jwt_extended.create_access_token(
            additional_claims={"tags": tags or []},
            expires_delta=expires_delta,
            identity=user.id,
        )
        token = cls(
            name=name,
            value=token_value,
            user=user,
        )
        db.session.add(token)
        db.session.commit()
        return token

    @classmethod
    def create_mfa_totp_token(cls, user, expires_delta=False) -> AuthToken:
        return cls.create(
            user,
            cls.TOTP_MFA_TAG,
            [cls.HIDDEN_TAG, cls.TOTP_MFA_TAG],
            expires_delta or timedelta(seconds=60),
        )

    @classmethod
    def create_mfa_webauthn_token(cls, user, expires_delta=False) -> AuthToken:
        return cls.create(
            user,
            cls.WEBAUTHN_MFA_TAG,
            [cls.HIDDEN_TAG, cls.WEBAUTHN_MFA_TAG],
            expires_delta or timedelta(seconds=60),
        )

    @classmethod
    def create_email_verification_token(cls, user, expires_delta=False) -> AuthToken:
        return cls.create(
            user,
            cls.VERIFY_EMAIL_TAG,
            [cls.HIDDEN_TAG, cls.VERIFY_EMAIL_TAG],
            expires_delta or timedelta(hours=24),
        )

    @classmethod
    def create_frontend_token(cls, user, expires_delta=False) -> AuthToken:
        """
        Creates an `AuthToken` used for the frontend to authenticate to the API.
        """
        return cls.create(
            user,
            cls.FRONTEND_TAG,
            [cls.HIDDEN_TAG, cls.FRONTEND_TAG],
            expires_delta,
        )

    @classmethod
    def create_reset_password_token(cls, user, expires_delta=False) -> AuthToken:
        return cls.create(
            user,
            cls.RESET_PASSWORD_TAG,
            [cls.HIDDEN_TAG, cls.RESET_PASSWORD_TAG],
            expires_delta or timedelta(hours=24),
        )

    @property
    def expires_in(self) -> Union[bool, timedelta]:
        try:
            claims = flask_jwt_extended.decode_token(self.value)
        except jwt.ExpiredSignatureError:
            # Token is expired
            return True
        else:
            # Token never expires
            if "exp" not in claims:
                return False
            else:
                return timedelta(seconds=claims["exp"] - time.time())

    @property
    def humanized_expires_in(self) -> str:
        match exp := self.expires_in:
            case True:
                return "Expired"
            case False:
                return "Never"
            case _:
                return humanize.naturaldelta(exp)

    @property
    def is_expired(self) -> bool:
        return self.expires_in is True

    @property
    def tags(self) -> List[str]:
        try:
            claims = flask_jwt_extended.decode_token(self.value)
        except jwt.ExpiredSignatureError:
            return []
        else:
            return claims.get("tags", [])

    def validate(self, require_tags=(), allow_expired=False) -> bool:
        return (not self.is_expired and not allow_expired) and set(require_tags).issubset(self.tags)


@sa.event.listens_for(db.session, "loaded_as_persistent")
def receive_loaded_as_persistent(session, instance):
    """Automatically delete expired `AuthToken` entries."""
    if isinstance(instance, AuthToken) and instance.is_expired:
        session.delete(instance)
        session.commit()
