from damavand.cloud.provider import AwsProvider
from damavand.factories import SparkControllerFactory

from applications.orders import CustomerOrders
from applications.products import Products


def main(arg) -> None:
    spark_factory = SparkControllerFactory(
        provider=AwsProvider(
            app_name="my-app",
            region="eu-west-1",
        ),
        tags={"env": "dev"},
        provision_on_creation=False,
    )

    spark_controller = spark_factory.new(
        name="my-spark",
    )

    spark_controller.applications = [
        Products(spark_controller.default_session()),
        CustomerOrders(spark_controller.default_session()),
    ]

    spark_controller.run_application(arg)
    spark_controller.provision()


if __name__ == "__main__":
    # arg_parser = ArgumentParser()
    # arg_parser.add_argument("--app_id", type=str, required=True)
    #
    # args = arg_parser.parse_args()

    # main(args)
    main("customer_orders")
