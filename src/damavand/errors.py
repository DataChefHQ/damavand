from typing import Optional


class DamavandException(Exception):
    fmt = "An unknown error occurred."

    def __init__(self, msg: Optional[str] = None, **kwargs: str) -> None:
        if msg is None:
            default_msg = self.fmt.format(**kwargs)
            super().__init__(default_msg)
        else:
            super().__init__(msg)


# Buildtime exceptions
class BuildtimeException(DamavandException):
    fmt = "An unknown error occurred during buildtime."


class CallResourceBeforeProvision(BuildtimeException):
    fmt = "Resource called before provision. Call `provision` method first."


class UnsupportedProvider(BuildtimeException):
    fmt = "The `{module}` has no implementation for this provider."


# Runtime exceptions
class RuntimeException(DamavandException):
    fmt = "An unknown error occurred happend during runtime."


class ResourceAccessDenied(RuntimeException):
    fmt = "Access to resource `{name}` is denied."


class ObjectNotFound(RuntimeException):
    fmt = "Object `{name}` not found in the storage."
