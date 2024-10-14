from damavand.cloud.provider import AwsProvider
from damavand.factories import SparkControllerFactory

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

    spark_controller = spark_factory.new(
        name="my-spark",
        applications=[
            Products(),
            CustomerOrders(),
        ],
    )
    # app_name = os.getenv("APP_NAME", "products-app")  # Get app name on runtime

    # spark_controller.run_application(app_name)
    spark_controller.provision()


if __name__ == "__main__":
    main()
