from typing import Optional
from pulumi import Resource as PulumiResource

from damavand import utils


def buildtime(func):
    def wrapper(self, *args, **kwargs):
        if not utils.is_building():
            return lambda _: None

        return func(self, *args, **kwargs)

    return wrapper


def runtime(func):
    def wrapper(self, *args, **kwargs):
        if utils.is_building():
            return lambda _: None

        return func(self, *args, **kwargs)

    return wrapper


class BaseResource(object):
    def __init__(
        self,
        name,
        id_: Optional[str] = None,
        tags: dict[str, str] = {},
        **kwargs,
    ) -> None:
        self.name = name
        self.tags = tags
        self.id_ = id_
        self.extra_args = kwargs
        self.__pulumi_object = None

    def provision(self):
        pass

    @buildtime
    def to_pulumi(self) -> PulumiResource:
        if not self.__pulumi_object:
            raise ValueError(
                "Resource not provisioned yet. Call `provision` method first."
            )

        return self.__pulumi_object
