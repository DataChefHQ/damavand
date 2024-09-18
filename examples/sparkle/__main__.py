from damavand.cloud.provider import AwsProvider
from damavand.factories import SparkControllerFactory

from applications.orders import CustomerOrders
from applications.products import Products


def main() -> None:
    spark_factory = SparkControllerFactory(
        provider=AwsProvider(
            app_name="my-app",
            region="us-west-2",
        ),
        tags={"env": "dev"},
    )

    spark_controller = spark_factory.new(
        name="my-spark",
    )

    spark_controller.applications = [
        Products(spark_controller.default_session()),
        CustomerOrders(spark_controller.default_session()),
    ]

    spark_controller.run_application("products")
    spark_controller.provision()


if __name__ == "__main__":
    main()
