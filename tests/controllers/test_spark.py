import pytest
from unittest.mock import patch
from _pytest.monkeypatch import MonkeyPatch

from damavand.controllers import SparkController
from damavand.sparkle.data_reader import (
    IcebergReader,
)
from damavand.sparkle.data_writer import IcebergWriter


@pytest.fixture
def spark_controller():
    return SparkController(
        name="test",
        reader=IcebergReader(database_name="dummy-database"),
        writer=IcebergWriter(),
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
