import pulumi

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
            jobs=[],
            sql_admin_username="kiarashk",
            sql_admin_password="lkjsf@123",
        ),
    )

    pulumi.export(
        "resource_group",
        pulumi.Output.all(spark.resource_group).apply(lambda x: x[0].name),
    )


if __name__ == "__main__":
    main()
