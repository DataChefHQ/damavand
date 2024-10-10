from sparkle.application import Sparkle
from sparkle.config import Config, IcebergConfig, TableConfig
from sparkle.writer.iceberg_writer import IcebergWriter
from sparkle.reader.table_reader import TableReader

from pyspark.sql import DataFrame


class Products(Sparkle):
    def __init__(self):
        super().__init__(
            config=Config(
                app_name="products",
                app_id="products-app",
                version="0.0.1",
                database_bucket="s3://test-bucket",
                checkpoints_bucket="s3://test-checkpoints",
                iceberg_output=IcebergConfig(
                    database_name="all_products",
                    database_path="",
                    table_name="products_v1",
                ),
                hive_table_input=TableConfig(
                    database="source_database",
                    table="products_v1",
                    bucket="",
                ),
            ),
            readers={"products": TableReader},
            writers=[
                IcebergWriter,
            ],
        )

    def process(self) -> DataFrame:
        return self.input["products"].read()
