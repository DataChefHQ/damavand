import logging
from functools import cache
from typing import Optional

import boto3
from botocore.exceptions import ClientError
from pulumi import Resource as PulumiResource

from damavand.base.controllers.llm import LlmController
from damavand.base.controllers.base_controller import runtime, buildtime
from damavand.cloud.aws.resources import AwsVllmComponent, AwsVllmComponentArgs
from damavand.errors import RuntimeException


logger = logging.getLogger(__name__)


class AwsLlmController(LlmController):
    def __init__(
        self,
        name,
        region: str,
        model: Optional[str] = None,
        tags: dict[str, str] = {},
        **kwargs,
    ) -> None:
        super().__init__(name, tags, **kwargs)
        self._parameter_store = boto3.client("ssm")
        self._model_name = model
        self._region = region

    @property
    def model_id(self) -> str:
        """Return the model name/ID."""

        return self._model_name or "microsoft/Phi-3-mini-4k-instruct"

    @property
    def _base_url_ssm_name(self) -> str:
        """Return the SSM parameter name for the base url."""

        return f"/damavand/{self.name}/endpoint/url"

    @property
    @runtime
    @cache
    def base_url(self) -> str:
        """
        Retrieve the base URL from the SSM parameter store.

        Returns
        -------
        str
            The base URL.

        Raises
        ------
        RuntimeException
            If the base URL cannot be retrieved from AWS.

        """

        try:
            response = self._parameter_store.get_parameter(
                Name=self._base_url_ssm_name,
            )

            return response["Parameter"]["Value"]
        except ClientError as e:
            raise RuntimeException(
                f"Failed to retrieve endpoint URL from SSM parameter store: {e}"
            )
        except KeyError as e:
            raise RuntimeException(
                f"Failed to retrieve endpoint URL from SSM parameter store: {e}"
            )

    @property
    @runtime
    @cache
    def chat_completions_url(self) -> str:
        """Return the chat completions URL."""

        return f"{self.base_url}/chat/completions"

    @property
    @runtime
    @cache
    def client(self) -> "openai.OpenAI":  # noqa # type: ignore
        """Return an OpenAI client."""

        try:
            import openai  # noqa # type: ignore
        except ImportError:
            raise RuntimeException(
                "Failed to import OpenAI library. Damavand provide this library as an optional dependency. Try to install it using `pip install damavand[openai]` or directly install it using pip or your dependency manager."
            )

        return openai.OpenAI(
            api_key="EMPTY",
            base_url=f"{self.base_url}",
        )

    @buildtime
    @cache
    def resource(self) -> PulumiResource:
        """Return the Pulumi IaC AwsVllmComponent object."""

        return AwsVllmComponent(
            name=self.name,
            args=AwsVllmComponentArgs(
                region=self._region,
                public_internet_access=True,
                endpoint_ssm_parameter_name=self._base_url_ssm_name,
            ),
        )
