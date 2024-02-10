__all__ = (
    "AppException",
    "ModeratorRequired",
    "TopicSubscribeRequestError",
)


class AppException(Exception):
    pass


class ModeratorRequired(AppException):
    pass


class TopicSubscribeRequestError(AppException):
    pass
