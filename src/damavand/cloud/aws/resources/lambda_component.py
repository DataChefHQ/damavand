import json
import os
from typing import Optional
from functools import cached_property
from dataclasses import dataclass

import pulumi
import pulumi_aws as aws
from pulumi import ResourceOptions
from pulumi import ComponentResource as PulumiComponentResource

from damavand.cloud.aws.resources.aws_services import AwsService


# TODO: rename to AwsServerlessPythonComponentArgs
@dataclass
class AwsLambdaComponentArgs:
    """
    Arguments for the AwsLambdaComponent component.

    ...

    Attributes
    ----------
    permissions : list[aws.iam.ManagedPolicy]
        the managed policies for the Lambda function.
    python_site_packages_path : Optional[str]
        the path to the python site packages. Default is `./venv/lib/python<SELECTED VERSION>/site-packages`.
    python_site_packages_bucket : Optional[aws.s3.Bucket]
        the S3 bucket for the python site packages. If not provided, a new bucket will be created.
    python_version : str | aws.lambda_.Runtime
        the python version for the Lambda function. Default is `aws.lambda_.Runtime.PYTHON3D12`.
    handler : str
        the handler for the Lambda function. Default is `__main__.event_handler`.
    handler_root_directory : str
        the root directory for the handler. Default is current working directory.
    """

    permissions: list[aws.iam.ManagedPolicy] = []
    python_site_packages_path: Optional[str] = None
    python_site_packages_bucket: Optional[aws.s3.Bucket] = None
    python_version: str | aws.lambda_.Runtime = aws.lambda_.Runtime.PYTHON3D12
    handler: str = "__main__.event_handler"
    handler_root_directory: str = os.getcwd()
    # TODO: add support for vpc


class AwsLambdaComponent(PulumiComponentResource):
    """
    The AwsLambdaComponent class is a Pulumi component that deploys python applications into an AWS Lambda Function.

    ...

    Attributes
    ----------
    name : str
        the name of the component.
    args : AwsLambdaComponentArgs
        the arguments of the component.
    opts : Optional[ResourceOptions]
        the resource options.

    Methods
    -------
    """

    def __init__(
        self,
        name: str,
        args: AwsLambdaComponentArgs,
        opts: Optional[ResourceOptions] = None,
    ) -> None:
        super().__init__(
            f"Damavand:{AwsLambdaComponent.__name__}",
            name=name,
            props={},
            opts=opts,
            remote=False,
        )

        self.args = args
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
            code=pulumi.FileArchive(self.args.handler_root_directory),
            layers=[self.python_dependencies_lambda_layer.arn],
            timeout=300,
            memory_size=128,
        )

    # TODO: refactor to use pulumi bucket v2 for unique bucket names
    @cached_property
    def python_dependency_bucket(self) -> aws.s3.Bucket:
        """
        Return the S3 bucket for python dependencies.

        Returns
        -------
        aws.s3.Bucket
            the S3 bucket for python dependencies.
        """

        return self.args.python_site_packages_bucket or aws.s3.Bucket(
            resource_name=f"{self._name}-site-packages-bucket",
            opts=ResourceOptions(parent=self),
            bucket=f"{self._name}-py-site-packages",
            acl="private",
        )

    @cached_property
    def python_dependencies_s3_objects(self) -> aws.s3.BucketObject:
        """
        Return the S3 objects for python dependencies.

        Returns
        -------
        aws.s3.BucketObject
            the S3 objects for python dependencies.
        """

        site_packages_path = self.args.python_site_packages_path or os.path.join(
            self.args.handler_root_directory,
            f"venv/lib/{self.args.python_version}/site-packages",
        )

        return aws.s3.BucketObject(
            resource_name=f"{self._name}-site-packages-object",
            opts=ResourceOptions(parent=self),
            bucket=self.python_dependency_bucket.bucket,
            key=f"{self._name}/site-packages.zip",
            source=pulumi.FileArchive(site_packages_path),
        )

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
            opts=ResourceOptions(parent=self),
            layer_name=f"{self._name}-site-packages-layer",
            s3_bucket=self.python_dependencies_s3_objects.bucket,
            s3_key=self.python_dependencies_s3_objects.key,
        )
