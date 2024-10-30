import logging
from functools import cache
from typing import Optional

import boto3
from botocore.exceptions import ClientError

from damavand.base.controllers.llm import LlmController
from damavand.base.controllers.base_controller import CostManagement, runtime, buildtime
from damavand.errors import RuntimeException


logger = logging.getLogger(__name__)


class AwsLlmController(LlmController):
    """
    AWS implementation of the LLM Controller. You can check LlmController for more information.

    Parameters
    ----------
    name : str
        The name of the controller.
    region : str
        The AWS region.
    model : Optional[str]
        The model name or ID.
    tags : dict[str, str]

    Methods
    -------
    base_url
        Return the base URL for the LLM API.
    default_api_key
        Return the default API key.
    resource
        Return the Pulumi IaC AwsVllmComponent object.
    """

    def __init__(
        self,
        name,
        region: str,
        cost: CostManagement,
        model: Optional[str] = None,
        python_version: str = "python3.11",
        python_runtime_requirements_file: str = "../requirements-run.txt",
        tags: dict[str, str] = {},
        **kwargs,
    ) -> None:
        super().__init__(
            name,
            cost,
            model,
            python_version,
            python_runtime_requirements_file,
            tags,
            **kwargs,
        )
        self._parameter_store = boto3.client("ssm", region_name=region)
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
    def resource(self) -> "PulumiResource":  # type: ignore # noqa
        """Creates the necessary IaC resources for serving the LLM and hosting the python application."""

        from damavand.cloud.aws.resources.llm_app_component import (
            AwsLlmAppComponent,
            AwsServerlessPythonComponentArgs,
            AwsVllmComponentArgs,
        )

        return AwsLlmAppComponent(
            name=self.name,
            tags=self.all_tags,
            args=(
                AwsVllmComponentArgs(
                    region=self._region,
                    api_key_required=False,
                    endpoint_ssm_parameter_name=self._base_url_ssm_name,
                ),
                AwsServerlessPythonComponentArgs(
                    python_version=self._python_version,
                    python_requirements_file=self._python_runtime_requirements_file,
                ),
            ),
        )

    @buildtime
    @cache
    def cost_controls(self) -> "PulumiResource":  # type: ignore # noqa
        """Creates the necessary IaC resources for cost controls."""

        from damavand.cloud.aws.resources.budget_component import (
            AwsBudgetComponent,
            AwsBudgetComponentArgs,
        )

        return AwsBudgetComponent(
            name=self.name,
            tags=self.all_tags,
            args=AwsBudgetComponentArgs(
                montly_limit_in_dollors=self._cost.monthly_limit_in_dollars,
                subscriber_emails=self._cost.notification_subscribers,
                filter_tag_key="application",
                filter_tag_value=self.name,
            ),
        )
