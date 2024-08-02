from typing import Optional, Union
from pulumi_azure_native import Provider as PulumiAzurermProvider
from pulumi_aws import Provider as PulumiAwsProvider
from pulumi import ResourceOptions


class BaseProvider:
    def __init__(self, app_name: str) -> None:
        self.app_name = app_name


class AwsProvider(BaseProvider, PulumiAwsProvider):
    def __init__(
        self,
        app_name: str,
        region: str,
        opts: Optional[ResourceOptions] = None,
        **kwargs,
    ) -> None:
        """Create a new AWS provider instance. For available options, see: https://www.pulumi.com/registry/packages/aws/api-docs/provider/#inputs"""

        BaseProvider.__init__(
            self,
            app_name=app_name,
        )
        PulumiAwsProvider.__init__(
            self,
            resource_name=f"{app_name}-provider",
            opts=opts,
            region=region,
            **kwargs,
        )

        self.__region = region

    @property
    def enforced_region(self) -> str:
        """Region that enforced to all AWS operations"""
        return self.__region


class AzurermProvider(BaseProvider, PulumiAzurermProvider):
    def __init__(self, app_name: str, **kwargs) -> None:
        BaseProvider.__init__(
            self,
            app_name=app_name,
        )
        PulumiAzurermProvider.__init__(
            self,
            resource_name=f"{app_name}-provider",
            **kwargs,
        )


CloudProvider = Union[
    AwsProvider,
    AzurermProvider,
]
