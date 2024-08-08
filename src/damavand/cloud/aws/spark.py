import json
import logging
from dataclasses import dataclass
from typing import Optional
from functools import cache

import boto3

import pulumi_aws as aws
from pulumi import Resource as PulumiResource
from pulumi import ComponentResource as PulumiComponentResource
from pulumi import ResourceOptions

# TODO: The following import will be moved to a separated framework
from damavand.sparkle.data_reader import DataReader
from damavand.sparkle.data_writer import DataWriter

from damavand.controllers import SparkController
from damavand.controllers.base_controller import buildtime


logger = logging.getLogger(__name__)


class AwsSparkController(SparkController):
    def __init__(
        self,
        name,
        region: str,
        reader: DataReader,
        writer: DataWriter,
        id_: Optional[str] = None,
        tags: dict[str, str] = {},
        **kwargs,
    ) -> None:
        super().__init__(name, reader, writer, id_, tags, **kwargs)
        self.__glue_client = boto3.client("glue", region_name=region)

    @buildtime
    @cache
    def resource(self) -> PulumiResource:
        return GlueComponent(
            name=self.name,
        )


@dataclass
class GlueComponentArgs:
    role: Optional[aws.iam.Role] = None
    code_repository_bucket: Optional[aws.s3.BucketV2] = None


class GlueComponent(PulumiComponentResource):
    @staticmethod
    def assume_policy() -> dict:
        """Return the assume role policy for Glue jobs."""

        return {
            "Version": "2012-10-17",
            "Statement": [
                {
                    "Effect": "Allow",
                    "Principal": {
                        "Service": "glue.amazonaws.com",
                    },
                    "Action": "sts:AssumeRole",
                },
            ],
        }

    @staticmethod
    def managed_policy_arns() -> list[str]:
        """Return a list of managed policy ARNs that defines the permissions for Glue jobs."""

        return [
            aws.iam.ManagedPolicy.AWS_GLUE_SERVICE_ROLE,
            aws.iam.ManagedPolicy.AMAZON_S3_FULL_ACCESS,
            aws.iam.ManagedPolicy.CLOUD_TRAIL_FULL_ACCESS,
        ]

    def __init__(
        self,
        name: str,
        args: GlueComponentArgs = GlueComponentArgs(),
        opts: Optional[ResourceOptions] = None,
    ) -> None:
        super().__init__(
            f"Damavand:Spark:{GlueComponent.__name__}",
            name=f"{name}-glue-component",
            props={},
            opts=opts,
            remote=False,
        )

        self.args = args
        self.code_repository_bucket
        self.iceberg_database
        self.jobs

    @property
    @cache
    def role(self) -> aws.iam.Role:
        """Return an execution role for Glue jobs."""

        return self.args.role or aws.iam.Role(
            resource_name=f"{self._name}-role",
            opts=ResourceOptions(parent=self),
            name=f"{self._name}-ExecutionRole",
            assume_role_policy=json.dumps(self.assume_policy()),
            managed_policy_arns=self.managed_policy_arns(),
        )

    @property
    @cache
    def code_repository_bucket(self) -> aws.s3.BucketV2:
        """Return an S3 bucket for Glue jobs to host source codes."""

        # NOTE: using `bucket_prefix` to avoid name conflict as the bucket name must be globally unique.
        return self.args.code_repository_bucket or aws.s3.BucketV2(
            resource_name=f"{self._name}-code-bucket",
            opts=ResourceOptions(parent=self),
            bucket_prefix=f"{self._name}-code-bucket",
        )

    @property
    @cache
    def iceberg_bucket(self) -> aws.s3.BucketV2:
        """Return an S3 bucket for Iceberg tables to store data processed by Glue jobs."""

        # NOTE: using `bucket_prefix` to avoid name conflict as the bucket name must be globally unique.
        return aws.s3.BucketV2(
            resource_name=f"{self._name}-bucket",
            opts=ResourceOptions(parent=self),
            bucket_prefix=f"{self._name}-bucket",
        )

    @property
    @cache
    def iceberg_database(self) -> aws.glue.CatalogDatabase:
        """Return a Glue database for Iceberg tables to store data processed by Glue jobs."""

        return aws.glue.CatalogDatabase(
            resource_name=f"{self._name}-database",
            opts=ResourceOptions(parent=self),
            name=f"{self._name}-database",
            location_uri=f"s3://{self.iceberg_bucket.bucket}/",
        )

    @property
    @cache
    def jobs(self) -> list[aws.glue.Job]:
        """Return all the Glue jobs for the application."""

        return [
            aws.glue.Job(
                resource_name=f"{self._name}-job",
                opts=ResourceOptions(parent=self),
                name=f"{self._name}-job",
                role_arn=self.role.arn,
                glue_version="4.0",
                command={
                    "script_location": f"s3://{self.code_repository_bucket.bucket}/",
                },
            )
        ]