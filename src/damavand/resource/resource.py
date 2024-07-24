from typing import Optional
from cdktf import TerraformStack, TerraformResource

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


class Resource(object):
    def __init__(
        self,
        name,
        stack: TerraformStack,
        id_: Optional[str] = None,
        tags: dict[str, str] = {},
        **kwargs,
    ) -> None:
        self.name = name
        self.tags = tags
        self.id_ = id_
        self.stack = stack
        self.extra_args = kwargs
        self.__cdktf_object = None

    def provision(self):
        pass

    @buildtime
    def to_cdktf(self) -> TerraformResource:
        if not self.__cdktf_object:
            raise ValueError(
                "Resource not provisioned yet. Call `provision` method first."
            )

        return self.__cdktf_object
