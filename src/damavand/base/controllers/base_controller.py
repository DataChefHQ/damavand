import logging
from typing import Optional
from functools import cache
from pulumi import Resource as PulumiResource
import pulumi

from damavand import utils


logger = logging.getLogger(__name__)


def buildtime(func):
    def wrapper(self, *args, **kwargs):
        if not utils.is_building():
            return None

        return func(self, *args, **kwargs)

    return wrapper


def runtime(func):
    def wrapper(self, *args, **kwargs):
        if utils.is_building():
            return None

        return func(self, *args, **kwargs)

    return wrapper


class ApplicationController(object):
    def __init__(
        self,
        name: str,
        id: Optional[str] = None,
        tags: dict[str, str] = {},
        **kwargs,
    ) -> None:
        self.name = name
        self.tags = tags
        # FIXME: the id should be removed.
        self._id = id
        self.extra_args = kwargs
        self._pulumi_object = None

    @property
    @buildtime
    @cache
    def build_config(self) -> pulumi.Config:
        return pulumi.Config()

    @buildtime
    @cache
    def resource(self) -> PulumiResource:
        """A lazy property that provision the resource if it is not provisioned yet and return the pulumi object."""

        raise NotImplementedError()

    def provision(self) -> None:
        """Provision the resource in not provisioned yet."""

        _ = self.resource
