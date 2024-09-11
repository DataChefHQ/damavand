from sparkle.application import Sparkle
from sparkle.config import Config
from sparkle.writer.iceberg_writer import IcebergWriter

from pyspark.sql import DataFrame
from pyspark.sql import SparkSession


class Products(Sparkle):
    def __init__(self, spark_session: SparkSession):
        super().__init__(
            spark_session,
            config=Config(
                app_name="products",
                app_id="products",
                version="0.1",
                database_bucket="s3://bucket-name",
                kafka=None,
                input_database=None,
                output_database=None,
                iceberg_config=None,
                spark_trigger='{"once": True}',
            ),
            writers=[
                IcebergWriter(
                    database_name="default",
                    database_path="s3://bucket-name/warehouse",
                    table_name="products",
                )
            ],
        )

    def process(self) -> DataFrame:
        return self.input["products"].read()
