import pytest
from _pytest.monkeypatch import MonkeyPatch
from pyspark.sql import SparkSession, DataFrame

from damavand.sparkle.data_writer import DataWriter
from damavand.sparkle.data_reader import DataReader
from damavand.sparkle.models import InputField

from damavand.cloud.aws.controllers.spark import AwsSparkController, GlueComponent


class MockDataWriter(DataWriter):
    def write(self, df: DataFrame, spark_session: SparkSession) -> None:
        pass


class MockDataReader(DataReader):
    def read(
        self, inputs: list[InputField], spark_session: SparkSession
    ) -> dict[str, DataFrame]:
        return {}


@pytest.fixture
def controller():
    return AwsSparkController(
        "test-spark",
        reader=MockDataReader(),
        writer=MockDataWriter(),
        region="us-east-1",
    )


def test_resource_return_glue_component(
    controller: AwsSparkController, monkeypatch: MonkeyPatch
):
    monkeypatch.setenv("MODE", "BUILD")
    assert isinstance(controller.resource(), GlueComponent)
