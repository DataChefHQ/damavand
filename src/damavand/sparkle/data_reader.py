from typing import Protocol
from pyspark.sql import DataFrame, SparkSession

from .models import InputField


class DataReader(Protocol):
    def read(
        self, inputs: list[InputField], spark_session: SparkSession
    ) -> dict[str, DataFrame]: ...


class IcebergReader(DataReader):
    def __init__(self, database_name: str) -> None:
        super().__init__()
        self.database_name = database_name

    def read(
        self, inputs: list[InputField], spark_session: SparkSession
    ) -> dict[str, DataFrame]:
        raise NotImplementedError


class SqlReader(DataReader):
    def __init__(
        self,
        username: str,
        password: str,
        server_name: str = "localhost",
    ) -> None:
        super().__init__()
        self.username = username
        self.password = password
        self.server_name = server_name

    def read(
        self, inputs: list[InputField], spark_session: SparkSession
    ) -> dict[str, DataFrame]:
        raise NotImplementedError


class KafkaReader(DataReader):
    def __init__(self, server: str) -> None:
        super().__init__()
        self.server = server

    def read(
        self, inputs: list[InputField], spark_session: SparkSession
    ) -> dict[str, DataFrame]:
        for input in inputs:
            if _ := input.options.get("topic"):
                raise NotImplementedError
            else:
                raise ValueError(
                    "Option `topic` must be provided in the `InputField` with KafkaReader types."
                )

        raise NotImplementedError


class MultiDataReader(DataReader):
    def __init__(self, *readers: DataReader) -> None:
        super().__init__()
        self._readers = list(readers)

    def read(
        self, inputs: list[InputField], spark_session: SparkSession
    ) -> dict[str, DataFrame]:
        dataframes = {}

        for reader in self._readers:
            reader_inputs = [
                input for input in inputs if input.type == reader.__class__
            ]
            dfs = reader.read(reader_inputs, spark_session)
            dataframes.update(dfs)

        return dataframes
