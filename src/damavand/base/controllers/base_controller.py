from dataclasses import dataclass
import re
import logging
from functools import cache

from damavand import utils
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


@dataclass
class CostManagement:
    """Cost management configuration for the application.

    Parameters
    ----------
    notification_subscribers : list[str]
        List of email addresses to notify when the cost exceeds the limit.
    monthly_limit_in_dollars : int
        The monthly cost limit in dollars.
    """

    notification_subscribers: list[str]
    monthly_limit_in_dollars: int


class ApplicationController(object):
    def __init__(
        self,
        name: str,
        cost: CostManagement,
        tags: dict[str, str] = {},
        **kwargs,
    ) -> None:
        self.name = name
        self._userdefined_tags = tags
        self._cost = cost
        self.extra_args = kwargs

    @property
    def name(self) -> str:
        """Return the name of the controller."""

        return self._name

    @name.setter
    def name(self, value: str) -> None:
        """Set the name of the controller."""

        pattern = re.compile(r"^[a-z0-9-]+$")

        if not pattern.match(value):
            raise ValueError(
                f"Invalid name: `{value}`. Name must be lowercase letters, numbers, and hyphens."
            )

        self._name = value

    @buildtime
    @cache
    def resource(self) -> "PulumiResource":  # type: ignore # noqa
        """A lazy property that provision the resource if it is not provisioned yet and return the pulumi object."""

        raise NotImplementedError()

    @buildtime
    @cache
    def cost_controls(self) -> "PulumiResource":  # type: ignore # noqa
        """Apply cost controls to the resources."""

        raise NotImplementedError()

    @property
    def userdefined_tags(self) -> dict[str, str]:
        """Return the user-defined tags."""

        return self._userdefined_tags

    @property
    @buildtime
    def default_tags(self) -> dict[str, str]:
        """Return the default tags for the resources."""

        return {
            "application": self.name,
            "tool": "datachef:damavand",
        }

    @property
    def all_tags(self) -> dict[str, str]:
        """Return all tags for the resource."""

        return {**self.default_tags, **self.userdefined_tags}

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
        """Provision all the resources and apply cost controls."""

        _ = self.resource()
        _ = self.cost_controls()
