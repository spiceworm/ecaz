__all__ = (
    "EcazException",
    "ModeratorRequired",
)


class EcazException(Exception):
    pass


class ModeratorRequired(EcazException):
    pass
