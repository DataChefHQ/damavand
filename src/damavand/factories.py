from typing import Optional

from damavand.base.controllers.spark import SparkController
from damavand.base.factory import ApplicationControllerFactory
from damavand.cloud.aws.controllers import AwsSparkController
from damavand.cloud.azure.controllers import AzureSparkController


class SparkControllerFactory(ApplicationControllerFactory[SparkController]):
    def _new_aws_controller(
        self,
        name: str,
        region: str,
        id: Optional[str] = None,
        tags: dict[str, str] = {},
        **kwargs,
    ) -> SparkController:
        return AwsSparkController(
            name=name,
            region=region,
            id=id,
            tags=tags,
            **kwargs,
        )

    def _new_azure_controller(
        self, name: str, id: Optional[str] = None, tags: dict[str, str] = {}, **kwargs
    ) -> SparkController:
        return AzureSparkController(
            name=name,
            id=id,
            tags=tags,
            **kwargs,
        )
