import pulumi
import pulumi_azure_native as azure
from damavand.base.controllers.base_controller import buildtime
from damavand.cloud.provider import AwsProvider
from damavand.factories import SparkControllerFactory

from damavand.cloud.azure.resources import SynapseComponent, SynapseComponentArgs


# def main():
#     spark_factory = SparkControllerFactory(
#         provider=AwsProvider(
#             app_name="my-app",
#             region="us-west-2",
#         ),
#         tags={"env": "dev"},
#     )
#
#     spark = spark_factory.new(name="my-spark")


def main() -> None:
    spark = SynapseComponent(
        name="my-spark",
        args=SynapseComponentArgs(
            sql_admin_username="kiarashk",
            sql_admin_password="lkjsf@123",
            pipelines=[],
        ),
    )

    pulumi.export(
        "resource_group",
        pulumi.Output.all(spark.resource_group).apply(lambda x: x[0].name),
    )


if __name__ == "__main__":
    main()
