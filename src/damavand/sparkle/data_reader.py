from dataclasses import dataclass
from typing import Any, Protocol
from pyspark.sql import DataFrame, SparkSession


class DataReader(Protocol):
    def read(
        self, inputs: dict[str, Any], spark_session: SparkSession
    ) -> dict[str, DataFrame]: ...


class IcebergReader(DataReader):
    def __init__(self, database_name: str) -> None:
        super().__init__()
        self.database_name = database_name

    def read(
        self, inputs: dict[str, Any], spark_session: SparkSession
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
        self, inputs: dict[str, Any], spark_session: SparkSession
    ) -> dict[str, DataFrame]:
        raise NotImplementedError


class KafkaReader(DataReader):
    def __init__(self, server: str) -> None:
        super().__init__()
        self.server = server

    def read(
        self, inputs: dict[str, Any], spark_session: SparkSession
    ) -> dict[str, DataFrame]:
        raise NotImplementedError


@dataclass
class PrefixedDataReader:
    reader: DataReader
    prefix: str


class MultiReader(DataReader):
    def __init__(self, *readers: PrefixedDataReader) -> None:
        super().__init__()
        self._readers = list(readers)

    def read(
        self, inputs: dict[str, Any], spark_session: SparkSession
    ) -> dict[str, DataFrame]:
        dataframes = {}

        for key in inputs.keys():
            for prefixed_reader in self._readers:
                if key.startswith(prefixed_reader.prefix):
                    dataframes[key] = prefixed_reader.reader.read(inputs, spark_session)
                    break

        return dataframes
