import pytest
from unittest.mock import patch
from _pytest.monkeypatch import MonkeyPatch

from damavand.base.controllers import SparkController


@pytest.fixture
def spark_controller():
    return SparkController(
        name="test",
    )


def test_default_session(monkeypatch: MonkeyPatch, spark_controller: SparkController):
    monkeypatch.setenv("ENVIRONMENT", "local")

    with patch.object(spark_controller, "default_local_session") as mock_session:
        spark_controller.default_session()
        mock_session.assert_called_once()


@pytest.mark.parametrize(
    "environment",
    [
        "development",
        "production",
        "testing",
        "acceptance",
    ],
)
def test_default_session_with_environment(
    monkeypatch: MonkeyPatch,
    spark_controller: SparkController,
    environment: str,
):
    monkeypatch.setenv("ENVIRONMENT", environment)

    with patch.object(spark_controller, "default_cloud_session") as mock_session:
        spark_controller.default_session()
        mock_session.assert_called_once()
