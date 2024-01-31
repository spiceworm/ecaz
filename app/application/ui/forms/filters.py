__all__ = ("strip_whitespace",)


def strip_whitespace(value):
    if isinstance(value, str):
        return value.strip()
    return value
