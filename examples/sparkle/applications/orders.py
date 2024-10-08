from sparkle.config import Config, IcebergConfig, KafkaReaderConfig
from sparkle.config.kafka_config import KafkaConfig, Credentials
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
                iceberg_output=IcebergConfig(
                    database_name="all_products",
                    database_path="",
                    table_name="orders_v1",
                ),
                kafka_input=KafkaReaderConfig(
                    KafkaConfig(
                        bootstrap_servers="localhost:9119",
                        credentials=Credentials("test", "test"),
                    ),
                    kafka_topic="src_orders_v1",
                ),
            ),
            readers={"orders": KafkaReader},
            writers=[IcebergWriter],
        )

    def process(self) -> DataFrame:
        return self.input["orders"].read()
