from typing import Protocol
from pyspark.sql import DataFrame, SparkSession


class DataWriter(Protocol):
    def write(self, df: DataFrame, spark_session: SparkSession) -> None: ...


class MultiDataWriter(DataWriter):
    def __init__(self, *writers: DataWriter) -> None:
        super().__init__()
        self._writers = list(writers)

    def write(self, df: DataFrame, spark_session: SparkSession) -> None:
        for writer in self._writers:
            writer.write(df, spark_session)
