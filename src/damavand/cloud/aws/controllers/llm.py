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
        super().__init__(name, model, tags, **kwargs)
        self._parameter_store = boto3.client("ssm")
        self._region = region

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
    def default_api_key(self) -> str:
        """Return the default API key."""

        return "EMPTY"

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
