from typing import Protocol
from pyspark.sql import DataFrame, SparkSession


class DataWriter(Protocol):
    def write(self, df: DataFrame, spark_session: SparkSession) -> None: ...


class KafkaWriter(DataWriter):
    def write(self, df: DataFrame, spark_session: SparkSession) -> None:
        df.write.format("kafka").save()


class IcebergWriter(DataWriter):
    def write(self, df: DataFrame, spark_session: SparkSession) -> None:
        df.write.format("iceberg").save()


class MultiDataWriter(DataWriter):
    def __init__(self, *writers: DataWriter) -> None:
        super().__init__()
        self._writers = list(writers)

    def write(self, df: DataFrame, spark_session: SparkSession) -> None:
        for writer in self._writers:
            writer.write(df, spark_session)
