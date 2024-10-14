from sparkle.application import Sparkle
from damavand.base.controllers.spark import SparkController
from damavand.base.factory import ApplicationControllerFactory
from damavand.cloud.aws.controllers.spark import AwsSparkController
from damavand.cloud.azure.controllers import AzureSparkController


class SparkControllerFactory(ApplicationControllerFactory[SparkController]):
    def _new_aws_controller(
        self,
        name: str,
        applications: list[Sparkle],
        region: str,
        tags: dict[str, str] = {},
        **kwargs,
    ) -> SparkController:
        return AwsSparkController(
            name=name,
            applications=applications,
            region=region,
            tags=tags,
            **kwargs,
        )

    def _new_azure_controller(
        self,
        name: str,
        applications: list[Sparkle],
        tags: dict[str, str] = {},
        **kwargs,
    ) -> SparkController:
        return AzureSparkController(
            name=name,
            tags=tags,
            **kwargs,
        )
