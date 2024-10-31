import requests
import logging
from functools import cache
from typing import List, Optional

from damavand.base.controllers import ApplicationController
from damavand.base.controllers.base_controller import CostManagement, runtime
from damavand.errors import RuntimeException


logger = logging.getLogger(__name__)


class LlmController(ApplicationController):
    """
    Base class for LLM Controllers. This class provides the basic functionality for interacting with LLM APIs. The LLM APIs are following the OpenAI Chat Completions API model. For more information, see the [OpenAI documentation](https://platform.openai.com/docs/api-reference/chat/create).

    LLM Controllers are using vLLM as backend for hardware optimization and serving open source models. For available list of models, see the [vLLM documentation](https://docs.vllm.ai/en/latest/models/supported_models.html).

    Parameters
    ----------
    name : str
        The name of the controller.
    model : Optional[str]
        The model name or ID.
    tags : dict[str, str]

    Methods
    -------
    model_id
        Return the model name/ID.
    base_url
        Return the base URL for the LLM API.
    default_api_key
        Return the default API key.
    chat_completions_url
        Return the chat completions URL.
    client
       Return an OpenAI client as an standared interface for interacting with deployed LLM APIs.
    """

    def __init__(
        self,
        name,
        cost: CostManagement,
        model: Optional[str] = None,
        python_version: str = "python3.11",
        python_runtime_requirements_file: str = "../requirements-run.txt",
        tags: dict[str, str] = {},
        **kwargs,
    ) -> None:
        ApplicationController.__init__(self, name, cost, tags, **kwargs)
        self._model_name = model
        self._python_version = python_version
        self._python_runtime_requirements_file = python_runtime_requirements_file

    @property
    def model_id(self) -> str:
        """Return the model name/ID."""

        return self._model_name or "microsoft/Phi-3-mini-4k-instruct"

    @property
    @runtime
    @cache
    def base_url(self) -> str:
        """Return the base URL for the LLM API."""

        raise NotImplementedError

    @property
    @runtime
    @cache
    def default_api_key(self) -> str:
        """Return the default API key."""

        raise NotImplementedError

    @property
    @runtime
    @cache
    def chat_completions_url(self) -> str:
        """Return the chat completions URL."""

        return f"{self.base_url}/chat/completions"

    @runtime
    def create_chat(
        self,
        messages: List[dict],
        parameters: dict = {"max_new_tokens": 400},
        should_stream: bool = False,
    ) -> dict:
        """Create a chat completion."""

        headers = {
            "Content-Type": "application/json",
            "x-api-key": self.default_api_key,
        }

        json_data = {
            "messages": messages,
            "parameters": parameters,
            "stream": should_stream,
        }

        response = requests.post(
            self.chat_completions_url,
            headers=headers,
            json=json_data,
        )

        if response.status_code != 200:
            raise RuntimeException(
                f"Failed to create chat completion. Response: {response.json()}"
            )
        else:
            return response.json()
