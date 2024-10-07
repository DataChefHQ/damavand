from functools import cache
import logging
from typing import Optional

from damavand.base.controllers import ApplicationController
from damavand.base.controllers.base_controller import runtime
from damavand.errors import RuntimeException


logger = logging.getLogger(__name__)


class LlmController(ApplicationController):
    """ """

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
        """Return an OpenAI client."""

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
