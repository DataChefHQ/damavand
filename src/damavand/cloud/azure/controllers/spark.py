import logging
from functools import cache

import pulumi
from pulumi import Resource as PulumiResource

from sparkle.application import Sparkle

from damavand.base.controllers import buildtime
from damavand.base.controllers.base_controller import CostManagement
from damavand.base.controllers.spark import SparkController
from damavand.cloud.azure.resources import SynapseComponent, SynapseComponentArgs
from damavand.cloud.azure.resources.synapse_component import SynapseJobDefinition


logger = logging.getLogger(__name__)


class AzureSparkController(SparkController):
    def __init__(
        self,
        name,
        cost: CostManagement,
        applications: list[Sparkle],
        region: str,
        tags: dict[str, str] = {},
        **kwargs,
    ) -> None:
        super().__init__(name, cost, applications, tags, **kwargs)
        self.applications = applications

    @buildtime
    def admin_username(self) -> str:
        # FIXME: this has to be fixed
        return "admin"

    @buildtime
    @cache
    def admin_password(self) -> pulumi.Output[str] | str:
        # FIXME: this has to be fixed
        return "sample_password"

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
