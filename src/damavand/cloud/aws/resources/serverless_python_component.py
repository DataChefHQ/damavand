import json
import os
import logging
from typing import Optional
from functools import cached_property
from dataclasses import dataclass, field

import pulumi_aws as aws
import pulumi_command as command
from pulumi import FileArchive, FileAsset
from pulumi import ResourceOptions
from pulumi import ComponentResource as PulumiComponentResource

from damavand.cloud.aws.resources.aws_services import AwsService


logger = logging.getLogger(__name__)


# TODO: use google style docsting format
@dataclass
class AwsServerlessPythonComponentArgs:
    """
    Arguments for the AwsServerlessPythonComponent component.

    This component is using lambda function layer for python dependencies. The python dependencies are stored in an S3 bucket. The python dependencies are stored in a zip file. You can directly zip the site-packages directory of your virtual environment.
    ...

    Attributes
    ----------
    permissions: list[aws.iam.ManagedPolicy]
        the managed policies for the Lambda function.
    python_requirements_file: str
        the path to the requirements.txt file for the runtime environment.
    python_version: str | aws.lambda_.Runtime
        the python version for the Lambda function.
    handler: str
        the handler for the Lambda function. Default is `app.event_handler`.
    handler_root_directory: str
        the root directory of the handler to be uploaded to the Lambda function. Default is the `src` directory in the current working directory.
    """

    permissions: list[aws.iam.ManagedPolicy] = field(default_factory=list)
    python_requirements_file: str = "requirements-run.txt"
    python_version: str | aws.lambda_.Runtime = aws.lambda_.Runtime.PYTHON3D12
    handler: str = "app.event_handler"
    handler_root_directory: str = os.path.join(os.getcwd())
    # FIXME: this needs to be integrated when we have working DLZ that provides VPC
    subnet_ids: Optional[list[str]] = None
    security_group_ids: Optional[list[str]] = None


class AwsServerlessPythonComponent(PulumiComponentResource):
    """
    The AwsServerlessPythonComponent class is a Pulumi component that deploys python applications into an AWS Lambda Function.

    ...

    Attributes
    ----------
    name: str
        the name of the component.
    args: AwsServerlessPythonComponentArgs
        the arguments of the component.
    opts: Optional[ResourceOptions]
        the resource options.

    Methods
    -------
    """

    def __init__(
        self,
        name: str,
        tags: dict[str, str],
        args: AwsServerlessPythonComponentArgs,
        opts: Optional[ResourceOptions] = None,
    ) -> None:
        super().__init__(
            f"Damavand:{AwsServerlessPythonComponent.__name__}",
            name=name,
            props={},
            opts=opts,
            remote=False,
        )

        self.args = args
        self._tags = tags

        _ = self.runtime_env_builder
        _ = self.lambda_function

    @property
    def permissions(self) -> list[aws.iam.ManagedPolicy]:
        """
        Return the managed policies for the Lambda function.

        Returns
        -------
        list[aws.iam.ManagedPolicy]
            the managed policies for the Lambda function.
        """

        return [
            aws.iam.ManagedPolicy.AWS_LAMBDA_BASIC_EXECUTION_ROLE,
            aws.iam.ManagedPolicy.AWS_LAMBDA_VPC_ACCESS_EXECUTION_ROLE,
            aws.iam.ManagedPolicy.SECRETS_MANAGER_READ_WRITE,
            aws.iam.ManagedPolicy.AMAZON_SSM_READ_ONLY_ACCESS,
            *self.args.permissions,
        ]

    @cached_property
    def role(self) -> aws.iam.Role:
        """
        Return the IAM role for the Lambda function.

        Returns
        -------
        aws.iam.Role
            the IAM role for the Lambda function.
        """

        return aws.iam.Role(
            resource_name=f"{self._name}-role",
            opts=ResourceOptions(parent=self),
            name=f"{self._name}-ExecutionRole",
            managed_policy_arns=self.permissions,
            assume_role_policy=json.dumps(AwsService.LAMBDA.get_assume_policy()),
            tags=self._tags,
        )

    @cached_property
    def vpc_config(self) -> aws.lambda_.FunctionVpcConfigArgs | None:
        """
        Return the VPC configuration for the Lambda function.

        Returns
        -------
        aws.lambda.FunctionVpcConfigArgs
            the VPC configuration for the Lambda function.
        """

        if not self.args.subnet_ids:
            logger.warning(
                "No subnet IDs provided for the Lambda function. Skipping VPC configuration."
            )
            return None

        if not self.args.security_group_ids:
            logger.warning(
                "No security group IDs provided for the Lambda function. Skipping VPC configuration."
            )
            return None

        return aws.lambda_.FunctionVpcConfigArgs(
            subnet_ids=self.args.subnet_ids,
            security_group_ids=self.args.security_group_ids,
        )

    @cached_property
    def lambda_function(self) -> aws.lambda_.Function:
        """
        Return the Lambda function.

        Returns
        -------
        aws.lambda.Function
            the Lambda function.
        """

        return aws.lambda_.Function(
            resource_name=f"{self._name}-function",
            opts=ResourceOptions(parent=self),
            role=self.role.arn,
            handler=self.args.handler,
            runtime=self.args.python_version,
            code=FileArchive(self.args.handler_root_directory),
            layers=[self.python_dependencies_lambda_layer.arn],
            timeout=300,
            memory_size=128,
            vpc_config=self.vpc_config,
            tags=self._tags,
        )

    @cached_property
    def runtime_env_directory(self) -> str:
        """
        Create a temporary directory to cache and package the python dependencies.

        Returns
        -------
        str
            the path of the python dependencies.
        """

        path = os.path.join("/tmp", "damavand-artifacts", "deps", "python")
        os.makedirs(path, exist_ok=True)
        return path

    @cached_property
    def runtime_env_builder(self) -> command.local.Command:
        """
        Build the runtime environment for the Lambda function.

        Returns
        -------
        command.local.Command
            the command to build the runtime environment.
        """

        return command.local.Command(
            resource_name=f"{self._name}-runtime-env-builder",
            opts=ResourceOptions(parent=self),
            create=";".join(
                [
                    f"rm -rf {self.runtime_env_directory}",
                    f"pip install -r {self.args.python_requirements_file} --target {self.runtime_env_directory}",
                ]
            ),
            asset_paths=[self.runtime_env_directory],
            triggers=[
                FileArchive("/tmp/damavand-artifacts"),
                FileAsset(self.args.python_requirements_file),
            ],
        )

    @cached_property
    def runtime_env_artifacts(self) -> FileArchive:
        """
        Package the cached python dependencies into a zip file.

        Returns
        -------
        FileArchive
            the FileArchive of the runtime environment.
        """

        return FileArchive(os.path.dirname(self.runtime_env_directory))

    @cached_property
    def python_dependencies_lambda_layer(self) -> aws.lambda_.LayerVersion:
        """
        Return the Lambda layer with installed python dependencies files.

        Returns
        -------
        aws.lambda.LayerVersion
            the Lambda layer for python dependencies.
        """

        return aws.lambda_.LayerVersion(
            resource_name=f"{self._name}-site-packages-layer",
            opts=ResourceOptions(parent=self, depends_on=[self.runtime_env_builder]),
            layer_name=f"{self._name}-site-packages-layer",
            code=self.runtime_env_artifacts,
        )
