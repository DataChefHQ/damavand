from functools import cache
import logging
from typing import Optional

from damavand.base.controllers import ApplicationController
from damavand.base.controllers.base_controller import runtime
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
        model: Optional[str] = None,
        tags: dict[str, str] = {},
        **kwargs,
    ) -> None:
        ApplicationController.__init__(self, name, tags, **kwargs)
        self._model_name = model

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

    @property
    @runtime
    @cache
    def client(self) -> "openai.OpenAI":  # type: ignore # noqa
        """Return an OpenAI client as an standared interface for interacting with deployed LLM APIs."""
        # FIXME: the openai package must be installed via llm group. This is a temporary solution.

        try:
            import openai  # type: ignore # noqa
        except ImportError:
            raise RuntimeException(
                "Failed to import OpenAI library. Damavand provide this library as an optional dependency. Try to install it using `pip install damavand[openai]` or directly install it using pip or your dependency manager."
            )

        return openai.OpenAI(
            api_key=self.default_api_key,
            base_url=f"{self.base_url}",
        )
