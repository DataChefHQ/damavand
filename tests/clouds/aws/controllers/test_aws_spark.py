import pytest
from _pytest.monkeypatch import MonkeyPatch
from unittest.mock import Mock

from sparkle.application import Sparkle
from sparkle.config import Config

from damavand.cloud.aws.controllers.spark import AwsSparkController, GlueComponent


class MockSparkle(Sparkle):
    pass


@pytest.fixture
def controller():
    mock_sparkle = Mock(spec=Sparkle)
    mock_sparkle.config = Config(
        app_name="test-spark",
        app_id="test-spark",
        version="0.0.1",
        database_bucket="test-bucket",
        kafka=None,
        input_database=None,
        output_database=None,
        iceberg_config=None,
    )

    ctr = AwsSparkController(
        "test-spark",
        applications=[mock_sparkle],
        region="us-east-1",
    )

    return ctr


def test_resource_return_glue_component(
    controller: AwsSparkController, monkeypatch: MonkeyPatch
):
    monkeypatch.setenv("MODE", "BUILD")
    assert isinstance(controller.resource(), GlueComponent)
