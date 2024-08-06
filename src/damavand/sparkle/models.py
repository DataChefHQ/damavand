import os
from enum import Enum, StrEnum
from typing import Optional, Callable, Any
from dataclasses import dataclass


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


class TriggerMethod(Enum):
    PROCESS = "process"
    REPROCESS = "reprocess"
    OPTIMIZE = "optimize"

    @classmethod
    def all(cls) -> list["TriggerMethod"]:
        return [e for e in cls]

    @classmethod
    def all_values(cls) -> list[str]:
        return [e.value for e in cls]


@dataclass
class Pipeline:
    name: str
    func: Callable
    description: Optional[str] = None
    inputs: dict[str, str] = {}


@dataclass
class Trigger:
    method: TriggerMethod
    pipeline_name: str
    environment: Environment
    options: dict[str, Any]
