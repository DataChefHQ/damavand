import logging
from typing import Optional
from functools import cache

import pulumi
from pulumi import Resource as PulumiResource

from sparkle.application import Sparkle

from damavand.base.controllers import SparkController, buildtime
from damavand.cloud.azure.resources import SynapseComponent, SynapseComponentArgs
from damavand.cloud.azure.resources.synapse_component import SynapseJobDefinition


logger = logging.getLogger(__name__)


class AzureSparkController(SparkController):
    def __init__(
        self,
        name,
        region: str,
        id_: Optional[str] = None,
        tags: dict[str, str] = {},
        **kwargs,
    ) -> None:
        super().__init__(name, id_, tags, **kwargs)
        self.applications: list[Sparkle]

    @buildtime
    def admin_username(self) -> str:
        return self.build_config.require("admin_username")

    @buildtime
    @cache
    def admin_password(self) -> pulumi.Output[str] | str:
        return self.build_config.require_secret("admin_password")

    @buildtime
    @cache
    def resource(self) -> PulumiResource:
        return SynapseComponent(
            name=self.name,
            args=SynapseComponentArgs(
                jobs=[
                    SynapseJobDefinition(
                        name=app.config.app_name,
                        description=app.config.__doc__ or "",
                    )
                    for app in self.applications
                ],
                sql_admin_username=self.admin_username(),
                sql_admin_password=self.admin_password(),
            ),
        )
