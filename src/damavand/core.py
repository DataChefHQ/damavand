import logging
from typing import Any, Optional, cast
from rich.console import Console
import pulumi_aws as aws
import pulumi_azure_native as azurerm

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
    ) -> None:
        if isinstance(provider, AwsProvider) and not provider.region:
            raise ValueError("AWS provider must have a region set.")

        self.app_name = app_name
        self.provider = provider
        self._resources = resources

    def provision_all_resources(self) -> None:
        """Provision all resources in the factory"""

        for resource in self._resources:
            resource.provision()

    def new_object_storage(self, name: str, tags: dict, **kwargs) -> BaseObjectStorage:
        match self.provider:
            case AwsProvider():
                resource = AwsBucket(
                    name,
                    region=cast(str, self.provider.region),
                    tags=tags,
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
    def from_aws_provider(app_name: str, region: str, **kwargs) -> "CloudConnection":
        """
        Create a connection for AWS provider.
        Check `AwsProvider` class for more information about the available arguments.
        """

        provider = AwsProvider(
            f"{app_name}-provider",
            args=aws.ProviderArgs(region=region, **kwargs),
        )

        return CloudConnection(ResourceFactory(app_name, provider))

    @staticmethod
    def from_azure_provider(app_name: str, **kwargs) -> "CloudConnection":
        """
        Create a connection for Azure provider.
        Check `AzurermProvider` class for more information about the available arguments.
        """

        provider = AzurermProvider(
            f"{app_name}-provider", args=azurerm.ProviderArgs(**kwargs)
        )

        return CloudConnection(ResourceFactory(app_name, provider))

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
