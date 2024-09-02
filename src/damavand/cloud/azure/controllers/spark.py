import logging
from typing import Optional
from functools import cache


import pulumi
from pulumi import Resource as PulumiResource

# TODO: The following import will be moved to a separated framework
from damavand.sparkle.data_reader import DataReader
from damavand.sparkle.data_writer import DataWriter

from damavand.base.controllers import SparkController, buildtime
from damavand.cloud.azure.resources import SynapseComponent, SynapseComponentArgs


logger = logging.getLogger(__name__)


class AzureSparkController(SparkController):
    def __init__(
        self,
        name,
        region: str,
        reader: DataReader,
        writer: DataWriter,
        id_: Optional[str] = None,
        tags: dict[str, str] = {},
        **kwargs,
    ) -> None:
        super().__init__(name, reader, writer, id_, tags, **kwargs)

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
                pipelines=list(self._pipelines.values()),
                sql_admin_username=self.admin_username(),
                sql_admin_password=self.admin_password(),
            ),
        )
