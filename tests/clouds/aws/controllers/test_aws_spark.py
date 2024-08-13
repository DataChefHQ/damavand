import pytest
from _pytest.monkeypatch import MonkeyPatch
from pyspark.sql import SparkSession, DataFrame

from damavand.sparkle.data_writer import DataWriter
from damavand.sparkle.data_reader import DataReader, KafkaReader
from damavand.sparkle.models import InputField, TriggerMethod

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
    ctr = AwsSparkController(
        "test-spark",
        reader=MockDataReader(),
        writer=MockDataWriter(),
        region="us-east-1",
    )

    ctr.add_pipeline_rule(
        pipeline_name="test-pipeline",
        description="Test pipeline",
        func=lambda **_: None,
        method=TriggerMethod.PROCESS,
        inputs=[InputField("test", KafkaReader, topic="test")],
        options={},
    )

    return ctr


def test_resource_return_glue_component(
    controller: AwsSparkController, monkeypatch: MonkeyPatch
):
    monkeypatch.setenv("MODE", "BUILD")
    assert isinstance(controller.resource(), GlueComponent)
