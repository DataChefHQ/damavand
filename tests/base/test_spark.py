import pytest

from damavand.base.controllers import SparkController


@pytest.fixture
def spark_controller():
    return SparkController(
        name="test",
        applications=[],
    )
