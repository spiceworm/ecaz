import base64
import io

import flask
import pyotp
import qrcode
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


__all__ = ("Totp",)


class Totp(db.Model):
    id: Mapped[int] = mapped_column(
        nullable=False,
        primary_key=True,
    )
    enabled = sa.Column(
        StringEncryptedType(
            type_in=sa.Boolean,
            key=get_encryption_key,
            padding="zeroes",
        ),
        default=False,
    )
    user: Mapped["User"] = relationship(
        back_populates="totp",
    )
    user_id: Mapped[int] = mapped_column(
        sa.ForeignKey("user.id"),
        nullable=False,
    )
    secret = sa.Column(
        StringEncryptedType(
            key=get_encryption_key,
            padding="pkcs5",
        ),
        default=pyotp.random_base32,
    )

    def generate_qr_code(self):
        qr = qrcode.QRCode(version=1, box_size=10, border=5)
        qr.add_data(self.uri)
        qr.make(fit=True)
        img = qr.make_image(fill_color='black', back_color='white')
        buffered = io.BytesIO()
        img.save(buffered)
        return base64.b64encode(buffered.getvalue()).decode("utf-8")

    @property
    def handler(self):
        return pyotp.TOTP(
            self.secret,
            issuer=flask.current_app.config["APP_NAME"],
            name=self.user.username,
        )

    @hybrid_property
    def uri(self):
        return self.handler.provisioning_uri()

    def verify(self, user_otp):
        return self.handler.verify(user_otp)
