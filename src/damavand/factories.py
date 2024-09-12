
from damavand.base.controllers.spark import SparkController
from damavand.base.factory import ApplicationControllerFactory
from damavand.cloud.aws.controllers import AwsSparkController
from damavand.cloud.azure.controllers import AzureSparkController


class SparkControllerFactory(ApplicationControllerFactory[SparkController]):
    def _new_aws_controller(
        self,
        name: str,
        region: str,
        tags: dict[str, str] = {},
        **kwargs,
    ) -> SparkController:
        return AwsSparkController(
            name=name,
            region=region,
            tags=tags,
            **kwargs,
        )

    def _new_azure_controller(
        self, name: str, tags: dict[str, str] = {}, **kwargs
    ) -> SparkController:
        return AzureSparkController(
            name=name,
            tags=tags,
            **kwargs,
        )
