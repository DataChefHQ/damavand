import logging
from typing import Any, Optional
from rich.console import Console

from damavand import utils
from damavand.resource import BaseResource, BaseObjectStorage
from damavand.cloud.provider import CloudProvider, AzurermProvider, AwsProvider
from damavand.cloud.aws import AwsBucket


logger = logging.getLogger(__name__)
console = Console()


class ResourceFactory:
    def __init__(
        self,
        app_name: str,
        provider: CloudProvider,
        resources: list[BaseResource] = [],
        tags: dict[str, str] = {},
    ) -> None:
        self.app_name = app_name
        self.provider = provider
        self._resources = resources
        self._user_defined_tags = tags

    @property
    def default_tags(self) -> dict[str, str]:
        return {
            "application": self.app_name,
            "environment": "development",
            "iac_optimizer": "damavand",
        }

    @property
    def user_defined_tags(self) -> dict[str, str]:
        return self._user_defined_tags

    @property
    def all_tags(self) -> dict[str, str]:
        return {
            **self.default_tags,
            **self.user_defined_tags,
        }

    def provision_all_resources(self) -> None:
        """Provision all resources in the factory"""

        for resource in self._resources:
            resource.provision()

    def new_object_storage(self, name: str, tags: dict, **kwargs) -> BaseObjectStorage:
        match self.provider:
            case AwsProvider():
                resource = AwsBucket(
                    name,
                    region=self.provider.enforced_region,
                    tags={**self.all_tags, **tags},
                    **kwargs,
                )
                self._resources.append(resource)
                return resource
            case AzurermProvider():
                raise NotImplementedError("Azure bucket is not implemented yet")
            case _:
                raise Exception("Unknown provider")


class CloudConnection:
    @staticmethod
    def from_aws_provider(
        app_name: str, region: str, tags: dict[str, str], **kwargs
    ) -> "CloudConnection":
        """
        Create a connection for AWS provider.
        Check `AwsProvider` class for more information about the available arguments.
        """

        provider = AwsProvider(
            app_name=app_name,
            region=region,
            **kwargs,
        )

        return CloudConnection(
            ResourceFactory(
                app_name=app_name,
                provider=provider,
                tags=tags,
            )
        )

    @staticmethod
    def from_azure_provider(
        app_name: str, tags: dict[str, str], **kwargs
    ) -> "CloudConnection":
        """
        Create a connection for Azure provider.
        Check `AzurermProvider` class for more information about the available arguments.
        """

        provider = AzurermProvider(
            app_name=app_name,
        )

        return CloudConnection(
            ResourceFactory(
                app_name=app_name,
                provider=provider,
                tags=tags,
                **kwargs,
            )
        )

    def __init__(self, resource_factory: ResourceFactory) -> None:
        self.resource_factory = resource_factory
        logger.warning(
            f"Running in {'build' if utils.is_building() else 'runtime'} mode"
        )

    def synth(self):
        self.resource_factory.provision_all_resources()

    def run(self, app: Optional[Any] = None) -> None:
        if utils.is_building():
            self.synth()
        else:
            pass
