import os
from typing import Optional
from cdktf import TerraformStack, TerraformResource

from damavand.stage import ResourceStage


IS_BUILDING = os.environ.get("MODE", "RUN") == "BUILD"


def buildtime(func):
    def wrapper(self, *args, **kwargs):
        if not IS_BUILDING:
            return lambda _: None

        return func(self, *args, **kwargs)

    return wrapper


def runtime(func):
    def wrapper(self, *args, **kwargs):
        if IS_BUILDING:
            return lambda _: None

        return func(self, *args, **kwargs)

    return wrapper


class Resource(object):
    def __init__(
        self,
        name,
        stack: TerraformStack,
        stage: ResourceStage,
        id_: Optional[str] = None,
        tags: dict[str, str] = {},
        **kwargs,
    ) -> None:
        self.name = name
        self.tags = tags
        self.id_ = id_
        self.stack = stack
        self.extra_args = kwargs
        self.stage = stage
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
