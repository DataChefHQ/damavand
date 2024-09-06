from typing import Optional
from functools import cache
from dataclasses import dataclass

import pulumi
import pulumi_azure_native as azure
from pulumi import ComponentResource as PulumiComponentResource
from pulumi import ResourceOptions

from damavand import utils


@dataclass
class SynapseJobDefinition:
    name: str
    description: str


@dataclass
class SynapseComponentArgs:
    jobs: list[SynapseJobDefinition]
    sql_admin_username: str
    sql_admin_password: str | pulumi.Output[str]
    storage_account: Optional[azure.storage.StorageAccount] = None


class SynapseComponent(PulumiComponentResource):
    def __init__(
        self,
        name: str,
        args: SynapseComponentArgs,
        opts: Optional[ResourceOptions] = None,
    ) -> None:
        super().__init__(
            f"Damavand:Spark:{SynapseComponent.__name__}",
            name=name,
            props={},
            opts=opts,
            remote=False,
        )

        self._args = args
        self._name = name
        self.spark_pool

    @property
    @cache
    def resource_group(self) -> azure.resources.ResourceGroup:
        """Create a resource group to hold all spark application resources."""

        return azure.resources.ResourceGroup(
            f"{self._name}-rg",
            resource_group_name=f"{self._name}-rg",
            location="westeurope",
            opts=ResourceOptions(parent=self),
        )

    @property
    @cache
    def storage_account(self) -> azure.storage.StorageAccount:
        return self._args.storage_account or azure.storage.StorageAccount(
            f'{self._name.replace("-", "").replace("_", "")}sa',
            resource_group_name=self.resource_group.name,
            access_tier=azure.storage.AccessTier.HOT,
            enable_https_traffic_only=True,
            kind=azure.storage.Kind.STORAGE_V2,
            sku=azure.storage.SkuArgs(
                name=azure.storage.SkuName.STANDARD_RAGRS,
            ),
            opts=ResourceOptions(parent=self),
        )

    @property
    @cache
    def storage_account_url(self) -> pulumi.Output[str]:
        return self.storage_account.name.apply(
            lambda name: f"https://{name}.dfs.core.windows.net"
        )

    @property
    @cache
    def users(self) -> azure.storage.BlobContainer:
        return azure.storage.BlobContainer(
            f"{self._name}users",
            resource_group_name=self.resource_group.name,
            account_name=self.storage_account.name,
            public_access=azure.storage.PublicAccess.NONE,
        )

    @property
    @cache
    def workspace(self) -> azure.synapse.Workspace:
        return azure.synapse.Workspace(
            f"{self._name}-ws",
            resource_group_name=self.resource_group.name,
            default_data_lake_storage=azure.synapse.DataLakeStorageAccountDetailsArgs(
                account_url=self.storage_account_url,
                filesystem="users",
            ),
            identity=azure.synapse.ManagedIdentityArgs(
                type=azure.synapse.ResourceIdentityType.SYSTEM_ASSIGNED,
            ),
            sql_administrator_login=self._args.sql_admin_username,
            sql_administrator_login_password=self._args.sql_admin_password,
        )

    @property
    @cache
    def spark_pool(self) -> azure.synapse.BigDataPool:
        return azure.synapse.BigDataPool(
            f"{utils.to_camel_case(self._name)}Pool",
            resource_group_name=self.resource_group.name,
            workspace_name=self.workspace.name,
            auto_pause=azure.synapse.AutoPausePropertiesArgs(
                delay_in_minutes=5,
                enabled=True,
            ),
            auto_scale=azure.synapse.AutoScalePropertiesArgs(
                enabled=True,
                max_node_count=3,
                min_node_count=3,
            ),
            node_count=3,
            node_size="Small",
            node_size_family="MemoryOptimized",
            spark_version="3.4",
        )

    # TODO: accesses needs to be reviewed and possibly add some implementation.
