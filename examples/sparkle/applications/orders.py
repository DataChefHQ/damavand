from sparkle.config import Config
from sparkle.writer.iceberg_writer import IcebergWriter
from sparkle.application import Sparkle

from pyspark.sql import DataFrame
from pyspark.sql import SparkSession


class CustomerOrders(Sparkle):
    def __init__(self, spark_session: SparkSession):
        super().__init__(
            spark_session,
            config=Config(
                app_name="orders",
                app_id="orders-app",
                version="0.0.1",
                database_bucket="s3://test-bucket",
                checkpoints_bucket="s3://test-checkpoints",
            ),
            writers=[
                IcebergWriter(
                    database_name="default",
                    database_path="s3://bucket-name/warehouse",
                    table_name="products",
                    spark_session=spark_session,
                )
            ],
        )

    def process(self) -> DataFrame:
        return self.input["orders"].read()
