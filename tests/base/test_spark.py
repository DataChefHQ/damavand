import pytest

from damavand.base.controllers.spark import SparkController


@pytest.fixture
def spark_controller():
    return SparkController(
        name="test",
        applications=[],
    )
