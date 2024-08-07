import logging
from typing import Optional, Callable
from pyspark.sql import SparkSession

from .models import Pipeline, Trigger, InputField
from .data_reader import DataReader
from .data_writer import DataWriter


logger = logging.getLogger(__name__)


class Sparkle:
    def __init__(self, reader: DataReader, writer: DataWriter) -> None:
        self.reader = reader
        self.writer = writer
        self.__pipelines: dict[str, Pipeline] = {}

    def add_pipeline_rule(
        self,
        pipeline_name: str,
        description: Optional[str],
        method: Callable,
        inputs: list[InputField],
    ):
        """Add a trigger rule for the given pipeline."""

        if pipeline_name in self.__pipelines.keys():
            raise RuntimeError(f"Pipeline `{pipeline_name}` is already defined.")
        else:
            self.__pipelines[pipeline_name] = Pipeline(
                name=pipeline_name,
                description=description,
                inputs=inputs,
                func=method,
            )

    def pipeline(self, name: str, inputs: list[InputField], **options) -> Callable:
        """A decorator to define an processing job for the given pipeline."""

        def decorator(func):
            self.add_pipeline_rule(
                pipeline_name=name,
                description=func.__doc__,
                method=func,
                inputs=inputs,
            )

            return func

        return decorator

    def run(self, trigger: Trigger, session: SparkSession) -> None:
        """Process a trigger request with the given Spark session."""

        logger.info(
            f"Pipeline `{trigger.pipeline_name}` is triggered with `{trigger.method}` method."
        )

        if requested_pipeline := self.__pipelines.get(trigger.pipeline_name):
            dataframes = self.reader.read(requested_pipeline.inputs, session)
            requested_pipeline.func(trigger, **dataframes)
        else:
            raise NotImplementedError(
                f"Pipeline `{trigger.pipeline_name}` is not defined."
            )
