import json
from typing import Any, Optional
from functools import cache
from dataclasses import dataclass, field

import pulumi_aws as aws
from pulumi import ComponentResource as PulumiComponentResource
from pulumi import ResourceOptions


@dataclass
class GlueJobDefinition:
    name: str
    description: str
    options: dict[str, Any] = field(default_factory=dict)


@dataclass
class GlueComponentArgs:
    jobs: list[GlueJobDefinition]
    role: Optional[aws.iam.Role] = None
    code_repository_bucket: Optional[aws.s3.BucketV2] = None


class GlueComponent(PulumiComponentResource):
    def __init__(
        self,
        name: str,
        args: GlueComponentArgs,
        opts: Optional[ResourceOptions] = None,
    ) -> None:
        super().__init__(
            f"Damavand:Spark:{GlueComponent.__name__}",
            name=name,
            props={},
            opts=opts,
            remote=False,
        )
        self.args = args

    @property
    def assume_policy(self) -> dict[str, Any]:
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

    @property
    def managed_policy_arns(self) -> list[str]:
        """Return a list of managed policy ARNs that defines the permissions for Glue jobs."""

        return [
            aws.iam.ManagedPolicy.AWS_GLUE_SERVICE_ROLE,
            aws.iam.ManagedPolicy.AMAZON_S3_FULL_ACCESS,
            aws.iam.ManagedPolicy.CLOUD_TRAIL_FULL_ACCESS,
        ]

    @property
    @cache
    def role(self) -> aws.iam.Role:
        """Return an execution role for Glue jobs."""

        return self.args.role or aws.iam.Role(
            resource_name=f"{self._name}-role",
            opts=ResourceOptions(parent=self),
            name=f"{self._name}-ExecutionRole",
            assume_role_policy=json.dumps(self.assume_policy),
            managed_policy_arns=self.managed_policy_arns,
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
                resource_name=f"{self._name}-{job.name}-job",
                opts=ResourceOptions(parent=self),
                name=f"{self._name}-{job.name}-job",
                role_arn=self.role.arn,
                glue_version="4.0",
                command={
                    "script_location": f"s3://{self.code_repository_bucket.bucket}/",
                },
                default_arguments={
                    "--env": "dev",
                    "--pipeline-name": job.name,
                    "--options": " ".join(
                        [f'{k}="{v}"' for k, v in job.options.items()]
                    ),
                },
            )
            for job in self.args.jobs
        ]

    def __add_kafka_connection(self, glue_job_name: str) -> aws.glue.Connection:
        """
        security_group = ec2.SecurityGroup(
            self,
            "GlueJobDefaultSecurityGroup",
            vpc=DEFAULT_VPC,
            allow_all_outbound=True,
            security_group_name="GlueJobDefaultSecurityGroup",
        )
        security_group.add_ingress_rule(
            peer=security_group,
            connection=ec2.Port.all_traffic(),
            description="Glue connection needs all of the ports to be open; Otherwise it will fail",
        )

        glue_connection = glue_alpha.Connection(
            self,
            "CompactionJobGlueConnection",
            type=glue_alpha.ConnectionType.KAFKA,
            connection_name=f"{construct_id}JobGlueConnection",
            description="Glue connection used by data product Glue jobs",
            subnet=ec2.Subnet.from_subnet_attributes(
                self,
                "GlueJobDefaultSubnet",
                subnet_id=retrieve_from_ssm_parameter(
                    self, "private_subnet_1_parameter_name"
                ),
                # WARN: this has not been parameterized in the ssm
                # parameter store. Also, not possible to retrieve
                # using cdk. Need to be solved by boto3 or something.
                availability_zone="eu-central-1a",
            ),
            security_groups=[security_group],
            properties={
                "KAFKA_BOOTSTRAP_SERVERS": kafka_credentials_secret.secret_value_from_json(
                    "bootstrap_servers"
                ).unsafe_unwrap(),
                "KAFKA_SASL_MECHANISM": "SCRAM-SHA-512",
                "KAFKA_SASL_SCRAM_USERNAME": kafka_credentials_secret.secret_value_from_json(
                    "kafka_username"
                ).unsafe_unwrap(),
                "KAFKA_SASL_SCRAM_PASSWORD": kafka_credentials_secret.secret_value_from_json(
                    "kafka_password"
                ).unsafe_unwrap(),
            },
        )
        """

        return aws.glue.Connection(
            resource_name=f"{self._name}-{glue_job_name}-kafka-connection",
            name=f"{self._name}-{glue_job_name}-kafka-connection",
            connection_type="KAFKA",
            connection_properties={
                "KAFKA_BOOTSTRAP_SERVERS": "your-kafka-bootstrap-servers",
                "KAFKA_SASL_MECHANISM": "SCRAM-SHA-512",
                "KAFKA_SASL_SCRAM_USERNAME": "your-username",  # Optional
                "KAFKA_SASL_SCRAM_PASSWORD": "your-password",  # Optional
            },
            physical_connection_requirements=aws.glue.ConnectionPhysicalConnectionRequirementsArgs(
                security_group_id_lists=["your-security-group-ids"],
                subnet_id="your-subnet-id",
            )
        )
