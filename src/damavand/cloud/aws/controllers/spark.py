import logging
from functools import cache
from typing import Any

import boto3
from pulumi import Resource as PulumiResource
from sparkle.application import Sparkle

from damavand.base.controllers import buildtime
from damavand.base.controllers.spark import SparkController
from damavand.cloud.aws.resources import GlueComponent
from damavand.errors import BuildtimeException


logger = logging.getLogger(__name__)


class AwsSparkController(SparkController):
    def __init__(
        self,
        name,
        applications: list[Sparkle],
        region: str,
        tags: dict[str, str] = {},
        resource_args: Any = None,
        **kwargs,
    ) -> None:
        super().__init__(name, applications, tags, **kwargs)
        self._glue_client = boto3.client("glue", region_name=region)
        self.resource_args = resource_args

    @buildtime
    @cache
    def resource(self) -> PulumiResource:
        if not self.applications:
            raise BuildtimeException("No applications found to create Glue jobs.")

        return GlueComponent(name=self.name, args=self.resource_args)
