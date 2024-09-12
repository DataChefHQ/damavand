import logging
from typing import Optional
from functools import cache

import boto3
from pulumi import Resource as PulumiResource

from damavand.base.controllers import SparkController, buildtime
from damavand.cloud.aws.resources import GlueComponent, GlueComponentArgs
from damavand.cloud.aws.resources.glue_component import GlueJobDefinition
from damavand.errors import BuildtimeException


logger = logging.getLogger(__name__)


class AwsSparkController(SparkController):
    def __init__(
        self,
        name,
        region: str,
        id_: Optional[str] = None,
        tags: dict[str, str] = {},
        **kwargs,
    ) -> None:
        super().__init__(name, id_, tags, **kwargs)
        self._glue_client = boto3.client("glue", region_name=region)

    @buildtime
    @cache
    def resource(self) -> PulumiResource:
        if not self.applications:
            raise BuildtimeException("No applications found to create Glue jobs.")

        return GlueComponent(
            name=self.name,
            args=GlueComponentArgs(
                jobs=[
                    GlueJobDefinition(
                        name=app.config.app_name,
                        description=app.config.__doc__ or "",
                    )
                    for app in self.applications
                ],
            ),
        )
