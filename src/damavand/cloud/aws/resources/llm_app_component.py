from functools import cached_property

from .vllm_component import AwsVllmComponent, AwsVllmComponentArgs
from .serverless_python_component import (
    AwsServerlessPythonComponent,
    AwsServerlessPythonComponentArgs,
)

from typing import Optional
from pulumi import ComponentResource as PulumiComponentResource
from pulumi import ResourceOptions


class AwsLlmAppComponent(PulumiComponentResource):
    """
    Creates necessary resources for an end-to-end LLM application. This includes a vLLM instance and a serverless Python application on AWS Lambda.

    Attributes:
        name: The unique name of the component.
        args: The arguments to configure the component.
        opts: Additional options to configure the component.

    """

    def __init__(
        self,
        name: str,
        args: tuple[AwsVllmComponentArgs, AwsServerlessPythonComponentArgs],
        opts: Optional[ResourceOptions] = None,
    ) -> None:
        super().__init__(
            f"Damavand:{AwsLlmAppComponent.__name__}",
            name=name,
            props={},
            opts=opts,
            remote=False,
        )

        self.__vllm_args = args[0]
        self.__serverless_python_args = args[1]

        _ = self.vllm
        _ = self.python_applet

    @cached_property
    def vllm(self) -> AwsVllmComponent:
        """
        Creates necessary resources for serving a vLLM instance.

        Returns:
            AwsVllmComponent: The vLLM component.
        """

        return AwsVllmComponent(
            name=f"{self._name}-vllm",
            args=self.__vllm_args,
            opts=ResourceOptions(parent=self),
        )

    @cached_property
    def python_applet(self) -> AwsServerlessPythonComponent:
        """Creates necessary resources for serverless serving a Python application.

        Returns:
            AwsServerlessPythonComponent: The serverless Python component.
        """

        return AwsServerlessPythonComponent(
            name=f"{self._name}-python-applet",
            args=self.__serverless_python_args,
            opts=ResourceOptions(parent=self),
        )
