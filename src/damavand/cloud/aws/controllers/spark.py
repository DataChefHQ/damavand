import logging
from typing import Optional
from functools import cache

import boto3

from pulumi import Resource as PulumiResource

# TODO: The following import will be moved to a separated framework
from damavand.sparkle.data_reader import DataReader
from damavand.sparkle.data_writer import DataWriter

from damavand.base.controllers import SparkController
from damavand.base.controllers.base_controller import buildtime
from damavand.cloud.aws.resources import GlueComponent


logger = logging.getLogger(__name__)


class AwsSparkController(SparkController):
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
        self.__glue_client = boto3.client("glue", region_name=region)

    @buildtime
    @cache
    def resource(self) -> PulumiResource:
        return GlueComponent(
            name=self.name,
        )
