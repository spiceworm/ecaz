import json
from typing import (
    ByteString,
    List,
)

import sqlalchemy as sa
from sqlalchemy.orm import (
    Mapped,
    mapped_column,
    relationship,
)
from sqlalchemy_utils import StringEncryptedType
import webauthn
from webauthn.helpers.structs import (
    PublicKeyCredentialDescriptor,
    PublicKeyCredentialType,
)

from application.models import (
    db,
    get_encryption_key,
)


__all__ = ("WebAuthn",)


def challenge_default() -> str:
    return webauthn.helpers.bytes_to_base64url(webauthn.helpers.generate_challenge())


def user_handle_default() -> str:
    return webauthn.helpers.bytes_to_base64url(webauthn.helpers.generate_user_handle())


class WebAuthn(db.Model):
    id: Mapped[int] = mapped_column(
        nullable=False,
        primary_key=True,
    )
    _challenge = sa.Column(
        StringEncryptedType(
            key=get_encryption_key,
            padding="pkcs5",
        ),
        default=challenge_default,
    )
    enabled = sa.Column(
        StringEncryptedType(
            type_in=sa.Boolean,
            key=get_encryption_key,
            padding="zeroes",
        ),
        default=False,
    )
    credential_sign_count = sa.Column(
        StringEncryptedType(
            type_in=sa.INTEGER,
            key=get_encryption_key,
            padding="oneandzeroes",
        ),
        default=0,
    )
    _public_key = sa.Column(
        StringEncryptedType(
            key=get_encryption_key,
            padding="pkcs5",
        ),
    )
    _registrations = sa.Column(
        StringEncryptedType(
            key=get_encryption_key,
            padding="pkcs5",
        ),
    )
    user: Mapped["User"] = relationship(
        back_populates="webauthn",
    )
    user_id: Mapped[int] = mapped_column(
        sa.ForeignKey("user.id"),
        nullable=False,
    )
    _user_handle = sa.Column(
        StringEncryptedType(
            key=get_encryption_key,
            padding="pkcs5",
        ),
        default=user_handle_default,
    )

    @property
    def challenge(self) -> ByteString:
        return webauthn.helpers.base64url_to_bytes(self._challenge)

    @property
    def public_key(self) -> ByteString:
        return webauthn.helpers.base64url_to_bytes(self._public_key)

    @public_key.setter
    def public_key(self, key) -> None:
        self._public_key = webauthn.helpers.bytes_to_base64url(key)

    @property
    def registrations(self) -> List[PublicKeyCredentialDescriptor]:
        retval = []
        if self._registrations:
            for obj in json.loads(self._registrations):
                obj["id"] = webauthn.helpers.base64url_to_bytes(obj["id"])
                obj["type"] = PublicKeyCredentialType(obj["type"])
                retval.append(PublicKeyCredentialDescriptor(**obj))
        return retval

    @registrations.setter
    def registrations(self, registrations) -> None:
        if registrations:
            for obj in registrations:
                obj["id"] = webauthn.helpers.bytes_to_base64url(obj["id"])
            self._registrations = json.dumps(registrations)

    @property
    def user_handle(self) -> ByteString:
        return webauthn.helpers.base64url_to_bytes(self._user_handle)
