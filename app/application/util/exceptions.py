__all__ = (
    "AppException",
    "ModeratorRequired",
)


class AppException(Exception):
    pass


class ModeratorRequired(AppException):
    pass
