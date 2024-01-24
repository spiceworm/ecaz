import os
import secrets

__all__ = (
    "Development",
    "Production",
    "Testing",
)


class _Config:
    TESTING = False


class Development(_Config):
    DEBUG = True
    SECRET_KEY = secrets.token_hex()


class Production(_Config):
    PROD = True
    SECRET_KEY = os.getenv("SECRET_KEY")


class Testing(_Config):
    TESTING = True
