import argparse
import logging
from typing import Protocol
from functools import cache

from .models import Trigger, Environment, TriggerMethod


logger = logging.getLogger(__name__)


class Application(Protocol):
    def run(self, trigger: Trigger) -> None: ...


class TriggerHandler(Protocol):
    def __init__(self, application: Application) -> None: ...
    def listen(self) -> None: ...


class ArgParsTriggerHandler(TriggerHandler):
    def __init__(self, application: Application) -> None:
        self.application = application

    @property
    @cache
    def parsed_args(self) -> argparse.Namespace:
        parser = argparse.ArgumentParser(
            description="Triggers pipelines of the SparkETL application.",
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
        )
        parser.add_argument(
            "--env",
            help="The environment to run the application in.",
            default=Environment.from_system_env().value,
            choices=Environment.all_values(),
            type=str,
        )
        parser.add_argument(
            "--pipeline-name",
            help="Name of the pipeline to be triggered.",
            required=True,
            type=str,
        )
        parser.add_argument(
            "--trigger-method",
            help="The trigger method of the pipeline.",
            choices=TriggerMethod.all_values(),
            required=True,
            type=str,
        )
        parser.add_argument(
            "--options",
            metavar="KEY=VALUE",
            nargs="+",
            help="Set a number of key-value pairs as trigger options (do not put spaces before or after the = sign). If a value contains spaces, you should define it with double quotes: 'foo=\"this is a sentence\". Note that ' values are always treated as strings.",
        )

        args, unknown = parser.parse_known_args()
        logger.warning(f"Unknown arguments: {unknown}")

        return args

    def listen(self) -> None:
        self.application.run(
            Trigger(
                pipeline_name=self.parsed_args.pipeline_name,
                environment=Environment(self.parsed_args.env),
                method=TriggerMethod(self.parsed_args.trigger_method),
                options={
                    "delete_before_reprocess": self.parsed_args.not_delete_before_reprocess,
                    **(
                        {
                            k: v
                            for k, v in (
                                arg.split("=") for arg in self.parsed_args.options
                            )
                        }
                        if self.parsed_args.options
                        else {}
                    ),
                },
            )
        )
