from typing import Union
from cdktf_cdktf_provider_aws.provider import AwsProvider
from cdktf_cdktf_provider_azurerm.provider import AzurermProvider

CloudProvider = Union[
    AwsProvider,
    AzurermProvider,
]
