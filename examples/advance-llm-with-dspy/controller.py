import dspy
from typing import Callable, Optional

from damavand.base.controllers.base_controller import runtime
from damavand.cloud.aws.controllers.llm import AwsLlmController

import applications


API_KEY = "EMPTY"


class AwsDspyController(AwsLlmController):
    def __init__(
        self,
        name,
        region: str,
        model: Optional[str] = None,
        tags: dict[str, str] = {},
        **kwargs,
    ) -> None:
        super().__init__(name, region, model, tags, **kwargs)
        self.applications: dict[str, Callable] = {
            "default": applications.default_question,
        }

    @property
    @runtime
    def connection(self) -> dspy.OpenAI:
        """Return the dspy OpenAI model."""

        return dspy.OpenAI(
            model=self.model_id,
            api_base=f"{self.base_url}/",
            api_key=API_KEY,
            model_type="chat",
        )

    @runtime
    def run_application(self, app_id: str, question: str, **kwargs) -> dict:
        """Run the specified application."""

        return self.applications[app_id](question, **kwargs)

    @runtime
    def build_or_run(self, **kwargs) -> None | dict:
        """
        Build or run the application based on the execution mode.

        Parameters
        ----------
        kwargs
            arguments to be passed to the application. Check the `run_application` method for more information.

        Returns
        -------
        None | dict
            If the execution mode is runtime, return the output of the application otherwise None.
        """

        if self.is_runtime_execution:
            self.run_application(**kwargs)
        else:
            self.provision()
