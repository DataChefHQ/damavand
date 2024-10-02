from sparkle.application import Sparkle
from sparkle.config import Config
from sparkle.writer.iceberg_writer import IcebergWriter
from sparkle.writer.kafka_writer import KafkaStreamPublisher
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
            ),
            readers={"products": TableReader},
            writers=[
                IcebergWriter,
                KafkaStreamPublisher,
            ],
        )

    def process(self) -> DataFrame:
        return self.input["products"].read()
