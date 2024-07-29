from typing import Union
from pulumi_azure_native import Provider as AzurermProvider
from pulumi_aws import Provider as AwsProvider


CloudProvider = Union[
    AwsProvider,
    AzurermProvider,
]
