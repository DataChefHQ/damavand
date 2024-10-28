import logging
from functools import cache

from damavand import utils
from damavand.base.resource import PulumiResource
from damavand.environment import Environment


logger = logging.getLogger(__name__)


def buildtime(func):
    def wrapper(self, *args, **kwargs):
        if not utils.is_building():
            logger.warning(
                f"Calling buildtime method `{func.__name__}` during runtime."
            )
            return None

        return func(self, *args, **kwargs)

    return wrapper


def runtime(func):
    def wrapper(self, *args, **kwargs):
        if utils.is_building():
            logger.warning(
                f"Calling runtime method `{func.__name__}` during buildtime."
            )
            return None

        return func(self, *args, **kwargs)

    return wrapper


class ApplicationController(object):
    def __init__(
        self,
        name: str,
        tags: dict[str, str] = {},
        **kwargs,
    ) -> None:
        self.name = name
        self.tags = tags
        self.extra_args = kwargs
        self._pulumi_object = None

    @buildtime
    @cache
    def resource(self) -> PulumiResource:
        """A lazy property that provision the resource if it is not provisioned yet and return the pulumi object."""

        raise NotImplementedError()

    @property
    def environment(self) -> Environment:
        """Return the environment that controller is being executed in."""

        if env := self.extra_args.get("environment"):
            return Environment(env)
        else:
            return Environment.from_system_env()

    @property
    def is_runtime_execution(self) -> bool:
        """Return True if the execution mode is runtime."""

        return not utils.is_building()

    def provision(self) -> None:
        """Provision the resource in not provisioned yet."""

        _ = self.resource()
