from sparkle.config import Config
from sparkle.writer.iceberg_writer import IcebergWriter
from sparkle.application import Sparkle
from sparkle.reader.kafka_reader import KafkaReader

from pyspark.sql import DataFrame


class CustomerOrders(Sparkle):
    def __init__(self):
        super().__init__(
            config=Config(
                app_name="orders",
                app_id="orders-app",
                version="0.0.1",
                database_bucket="s3://test-bucket",
                checkpoints_bucket="s3://test-checkpoints",
            ),
            readers={"orders": KafkaReader},
            writers=[IcebergWriter],
        )

    def process(self) -> DataFrame:
        return self.input["orders"].read()
