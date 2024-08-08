import os
from enum import StrEnum


class Environment(StrEnum):
    PRODUCTION = "production"
    DEVELOPMENT = "development"
    TESTING = "testing"
    ACCEPTANCE = "acceptance"
    LOCAL = "local"

    @classmethod
    def from_system_env(cls) -> "Environment":
        """Get the environment from the system environment variable."""

        env = os.environ.get("ENVIRONMENT", cls.LOCAL)
        return cls(env)

    @classmethod
    def all(cls) -> list["Environment"]:
        """Return all the environments."""

        return [env for env in cls]

    @classmethod
    def all_values(cls) -> list[str]:
        """Return all the environment values."""

        return [env.value for env in cls]
