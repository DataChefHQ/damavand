import pytest
from _pytest.monkeypatch import MonkeyPatch
from unittest.mock import Mock

from sparkle.application import Sparkle
from sparkle.config import Config

from damavand.base.controllers.base_controller import CostManagement
from damavand.cloud.aws.controllers.spark import AwsSparkController, GlueComponent
from damavand.errors import BuildtimeException


@pytest.fixture
def controller():
    ctr = AwsSparkController(
        "test-spark",
        applications=[],
        region="us-east-1",
        cost=CostManagement(
            notification_subscribers=[],
            monthly_limit_in_dollars=100,
        ),
    )

    return ctr


def test_resource_return_glue_component(
    controller: AwsSparkController, monkeypatch: MonkeyPatch
):
    monkeypatch.setenv("MODE", "BUILD")

    mock_sparkle = Mock(spec=Sparkle)
    mock_sparkle.config = Config(
        app_name="test-spark-app",
        app_id="test-spark-app-id",
        version="0.0.1",
        database_bucket="s3://test-bucket",
        checkpoints_bucket="s3://test-checkpoints",
    )

    controller.applications = [mock_sparkle]
    controller.provision()
    assert isinstance(controller.resource(), GlueComponent)


def test_should_throw_when_no_applications(
    controller: AwsSparkController, monkeypatch: MonkeyPatch
):
    monkeypatch.setenv("MODE", "BUILD")
    with pytest.raises(BuildtimeException):
        controller.provision()
