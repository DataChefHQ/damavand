import logging
from typing import Any, Optional
from cdktf_cdktf_provider_aws.provider import AwsProvider
from cdktf_cdktf_provider_azurerm.provider import AzurermProvider
from cdktf import TerraformStack, App
from rich.console import Console

from damavand import utils
from damavand.resource import Resource, IBucket, IFlaskServer
from damavand.cloud.provider import AzurermProvider, AwsProvider, CloudProvider
from damavand.cloud.aws import AwsBucket, AwsFlaskServer


logger = logging.getLogger(__name__)
console = Console()


class ResourceFactory:
    def __init__(
        self,
        app_name: str,
        tf_app: App,
        tf_stack: TerraformStack,
        provider: CloudProvider,
        resources: list[Resource] = [],
    ) -> None:
        self.app_name = app_name
        self.tf_app = tf_app
        # TODO: add option to have multiple stacks
        self.tf_stack = tf_stack
        self.provider = provider
        self._resources = resources

    def provision_all_resources(self) -> None:
        """Provision all resources in the factory"""

        for resource in self._resources:
            resource.provision()

    def new_bucket(self, name: str, tags: dict, **kwargs) -> IBucket:
        if isinstance(self.provider, AwsProvider):
            resource = AwsBucket(name, self.tf_stack, tags=tags, **kwargs)
            self._resources.append(resource)
            return resource
        elif isinstance(self.provider, AzurermProvider):
            raise NotImplementedError("Azure bucket is not implemented yet")
        else:
            raise Exception("Unknown provider")

    def new_flask_server(
        self,
        import_name: str,
        name: str,
        tags: dict,
        **kwargs,
    ) -> IFlaskServer:
        if isinstance(self.provider, AwsProvider):
            resource = AwsFlaskServer(
                import_name, name, self.tf_stack, tags=tags, **kwargs
            )
            self._resources.append(resource)
            return resource
        elif isinstance(self.provider, AzurermProvider):
            raise NotImplementedError("Azure flask server is not implemented yet")
        else:
            raise Exception("Unknown provider")


class CloudConnection:
    @staticmethod
    def from_aws_provider(app_name: str, region: str, **kwargs) -> "CloudConnection":
        """
        Create a connection for AWS provider.
        Check `AwsProvider` class for more information about the available arguments.
        """

        tf_app = App()
        tf_stack = TerraformStack(tf_app, app_name)
        provider = AwsProvider(tf_stack, f"{app_name}Stack", region=region, **kwargs)

        return CloudConnection(ResourceFactory(app_name, tf_app, tf_stack, provider))

    @staticmethod
    def from_azure_provider(app_name: str, **kwargs) -> "CloudConnection":
        """
        Create a connection for Azure provider.
        Check `AzurermProvider` class for more information about the available arguments.
        """

        tf_app = App()
        tf_stack = TerraformStack(tf_app, app_name)
        provider = AzurermProvider(tf_stack, f"{app_name}Stack", features={}, **kwargs)

        return CloudConnection(ResourceFactory(app_name, tf_app, tf_stack, provider))

    def __init__(self, resource_factory: ResourceFactory) -> None:
        self.resource_factory = resource_factory

    def synth(self):
        self.resource_factory.provision_all_resources()
        self.resource_factory.tf_app.synth()

    def run(self, app: Optional[Any] = None) -> None:
        if utils.is_building():
            self.synth()
        else:
            pass