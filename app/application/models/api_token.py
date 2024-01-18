from datetime import timedelta
import time

import flask_jwt_extended
import jwt
import sqlalchemy as sa
from sqlalchemy.ext.hybrid import hybrid_property
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


__all__ = ("ApiToken",)


class ApiToken(db.Model):
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
        back_populates="api_tokens",
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
    def create(cls, user, name, tags=None, expires_delta=False):
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
    def create_mfa_totp_token(cls, user, expires_delta=False):
        token = cls.create(
            user,
            cls.TOTP_MFA_TAG,
            [cls.HIDDEN_TAG, cls.TOTP_MFA_TAG],
            expires_delta or timedelta(seconds=60),
        )
        db.session.add(token)
        db.session.commit()
        return token

    @classmethod
    def create_mfa_webauthn_token(cls, user, expires_delta=False):
        token = cls.create(
            user,
            cls.WEBAUTHN_MFA_TAG,
            [cls.HIDDEN_TAG, cls.WEBAUTHN_MFA_TAG],
            expires_delta or timedelta(seconds=60),
        )
        db.session.add(token)
        db.session.commit()
        return token

    @classmethod
    def create_email_verification_token(cls, user, expires_delta=False):
        token = cls.create(
            user,
            cls.VERIFY_EMAIL_TAG,
            [cls.HIDDEN_TAG, cls.VERIFY_EMAIL_TAG],
            expires_delta or timedelta(hours=24),
        )
        db.session.add(token)
        db.session.commit()
        return token

    @classmethod
    def create_frontend_token(cls, user, expires_delta=False):
        """
        Creates an `ApiToken` used for the frontend to authenticate to the API.
        """
        token = cls.create(
            user,
            cls.FRONTEND_TAG,
            [cls.HIDDEN_TAG, cls.FRONTEND_TAG],
            expires_delta,
        )
        db.session.add(token)
        db.session.commit()
        return token

    @classmethod
    def create_reset_password_token(cls, user, expires_delta=False):
        token = cls.create(
            user,
            cls.RESET_PASSWORD_TAG,
            [cls.HIDDEN_TAG, cls.RESET_PASSWORD_TAG],
            expires_delta or timedelta(hours=24),
        )
        db.session.add(token)
        db.session.commit()
        return token

    @hybrid_property
    def expires_in(self):
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

    @hybrid_property
    def is_expired(self):
        return self.expires_in is True

    @hybrid_property
    def tags(self):
        try:
            claims = flask_jwt_extended.decode_token(self.value)
        except jwt.ExpiredSignatureError:
            return []
        else:
            return claims.get("tags", [])
