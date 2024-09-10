from argparse import ArgumentParser, Namespace
from damavand.cloud.provider import AwsProvider
from damavand.factories import SparkControllerFactory

from applications.orders import CustomerOrders
from examples.sparkle.applications.products import Products


def main(args: Namespace) -> None:
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

    spark_controller.run_application(id_=args.app_id)


if __name__ == "__main__":
    arg_parser = ArgumentParser()
    arg_parser.add_argument("--app_id", type=str, required=True)

    args = arg_parser.parse_args()

    main(args)
