from sparkle.application import Sparkle
from damavand.cloud.provider import AwsProvider
from damavand.factories import SparkControllerFactory
from damavand.cloud.aws.resources.glue_component import (
    GlueComponentArgs,
    GlueJobDefinition,
)

from applications.orders import CustomerOrders
from applications.products import Products


def main() -> None:

    spark_factory = SparkControllerFactory(
        provider=AwsProvider(
            app_name="my-app",
            region="eu-west-1",
        ),
        tags={"env": "dev"},
    )

    applications: list[Sparkle] = [Products(), CustomerOrders()]
    resource_args = GlueComponentArgs(
        jobs=[
            GlueJobDefinition(
                name=app.config.app_name,
                description=app.config.__doc__ or "",
                script_location="__main__.py",
                number_of_workers=2,
            )
            for app in applications
        ],
    )

    spark_controller = spark_factory.new(
        name="my-spark",
        applications=applications,
        resource_args=resource_args,
    )
    # app_name = os.getenv("APP_NAME", "products-app")  # Get app name on runtime

    # spark_controller.run_application(app_name)
    spark_controller.provision()


if __name__ == "__main__":
    main()
