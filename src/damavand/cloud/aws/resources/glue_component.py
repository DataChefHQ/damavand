import json
import logging
from typing import Any, Optional
from enum import Enum
from functools import cache
from dataclasses import dataclass, field

import pulumi_aws as aws
from pulumi import ComponentResource as PulumiComponentResource
from pulumi import ResourceOptions


class GlueWorkerType(Enum):
    G_1X: str = "G.1X"
    G_2X: str = "G.2X"
    G_4X: str = "G.4X"
    G_8X: str = "G.8X"
    G_025X: str = "G.025X"
    Z_2X: str = "Z.2X"


class GlueJobType(Enum):
    GLUE_ETL: str = "glueetl"
    GLUE_STREAMING: str = "gluestreaming"


class GlueExecutionClass(Enum):
    STANDARD: str = "STANDARD"
    FLEX: str = "FLEX"


class ConnectionType(Enum):
    KAFKA: str = "KAFKA"


@dataclass
class ConnectorConfig:
    """Configuration for the Connector.

    :param vpc_id: id of the vpc
    :param subnet_id: id of the subnet
    :param security_groups: list of security group ids
    :param connection_properties: a dictionary with connection properties specific to the connector.
        For more info see https://www.pulumi.com/registry/packages/aws/api-docs/glue/connection/
    """

    vpc_id: str
    subnet_id: str
    security_groups: list[str]
    connector_type: ConnectionType = ConnectionType.KAFKA
    connection_properties: dict = field(default_factory=list)


@dataclass
class GlueJobDefinition:
    """
    Parameters specific to the Glue job.

    :param name: The name you assign to this job. It must be unique in your account.
    :param description: Description of the job.
    :param script_location: the s3 path to the entrypoint script of your Glue application.
    :param extra_libraries: A list of paths to the extra dependencies. If you use packages not supported by Glue, compress them, upload them to s3 and pass here the path to the zip file.
    :param execution_class: Indicates whether the job is run with a standard or flexible execution class. The standard execution class is ideal for time-sensitive workloads that require fast job startup and dedicated resources. Valid value: `FLEX`, `STANDARD`.
    :param max_concurrent_runs: Max amount of instances of this Job that can run concurrently.
    :param glue_version: The version of glue to use, for example "1.0". Ray jobs should set this to 4.0 or greater. For information about available versions, see the [AWS Glue Release Notes](https://docs.aws.amazon.com/glue/latest/dg/release-notes.html).
    :param max_capacity: The maximum number of AWS Glue data processing units (DPUs) that can be allocated when this job runs. `Required` when `pythonshell` is set, accept either `0.0625` or `1.0`. Use `number_of_workers` and `worker_type` arguments instead with `glue_version` `2.0` and above.
    :param max_retries: The maximum number of times to retry this job if it fails.
    :param number_of_workers: The number of workers of a defined workerType that are allocated when a job runs.
    :param tags: Key-value map of resource tags. If configured with a provider `default_tags` configuration block present, tags with matching keys will overwrite those defined at the provider-level.
    :param timeout: The job timeout in minutes. The default is 2880 minutes (48 hours) for `glueetl` and `pythonshell` jobs, and null (unlimited) for `gluestreaming` jobs.
    :param worker_type: The type of predefined worker that is allocated when a job runs. Accepts a value of Standard, G.1X, G.2X, or G.025X for Spark jobs. Accepts the value Z.2X for Ray jobs.
           * For the Standard worker type, each worker provides 4 vCPU, 16 GB of memory and a 50GB disk, and 2 executors per worker.
           * For the G.1X worker type, each worker maps to 1 DPU (4 vCPU, 16 GB of memory, 64 GB disk), and provides 1 executor per worker. Recommended for memory-intensive jobs.
           * For the G.2X worker type, each worker maps to 2 DPU (8 vCPU, 32 GB of memory, 128 GB disk), and provides 1 executor per worker. Recommended for memory-intensive jobs.
           * For the G.4X worker type, each worker maps to 4 DPU (16 vCPUs, 64 GB of memory) with 256GB disk (approximately 235GB free), and provides 1 executor per worker. Recommended for memory-intensive jobs. Only available for Glue version 3.0. Available AWS Regions: US East (Ohio), US East (N. Virginia), US West (Oregon), Asia Pacific (Singapore), Asia Pacific (Sydney), Asia Pacific (Tokyo), Canada (Central), Europe (Frankfurt), Europe (Ireland), and Europe (Stockholm).
           * For the G.8X worker type, each worker maps to 8 DPU (32 vCPUs, 128 GB of memory) with 512GB disk (approximately 487GB free), and provides 1 executor per worker. Recommended for memory-intensive jobs. Only available for Glue version 3.0. Available AWS Regions: US East (Ohio), US East (N. Virginia), US West (Oregon), Asia Pacific (Singapore), Asia Pacific (Sydney), Asia Pacific (Tokyo), Canada (Central), Europe (Frankfurt), Europe (Ireland), and Europe (Stockholm).
           * For the G.025X worker type, each worker maps to 0.25 DPU (2 vCPU, 4GB of memory, 64 GB disk), and provides 1 executor per worker. Recommended for low volume streaming jobs. Only available for Glue version 3.0.
           * For the Z.2X worker type, each worker maps to 2 M-DPU (8vCPU, 64 GB of m emory, 128 GB disk), and provides up to 8 Ray workers based on the autoscaler.
    :param enable_glue_datacatalog: To use the Glue catalog as the metadata catalog
    :param enable_continuous_cloudwatch_log: To enable logging continuously.
    :param enable_continuous_log_filter: When set to true it reduces the amount of logging.
        For more information see https://repost.aws/knowledge-center/glue-reduce-cloudwatch-logs
    :param enable_metrics: Enables observability metrics about the worker nodes.
    :param enable_observability_metrics: Enables extra Spark-related observability metrics such as how long a tasks takes.
        This parameter could increase cloud costs significantly.
    :param script_args: The arguments that your own script consumes {"--arg1": "arg1 value"}
    :param schedule: A time-based cron-like schedule for the job. For syntax rules see https://docs.aws.amazon.com/glue/latest/dg/monitor-data-warehouse-schedule.html
    :param job_type: Specify if the job is streaming or batch.
    """

    # Parameters for Pulumi Glue Job
    name: str
    description: str = ""
    script_location: str = ""
    extra_libraries: list[str] = field(default_factory=list)
    execution_class: GlueExecutionClass = GlueExecutionClass.STANDARD
    max_concurrent_runs: int = 1
    glue_version: str = "4.0"
    enable_auto_scaling: bool = True
    max_capacity: int = 5
    max_retries: int = 0
    number_of_workers: int = 2
    tags: dict | None = None
    timeout: int = 2880
    worker_type: GlueWorkerType = GlueWorkerType.G_1X
    enable_glue_datacatalog: bool = True
    enable_continuous_cloudwatch_log: bool = False
    enable_continuous_log_filter: bool = True
    enable_metrics: bool = False
    enable_observability_metrics: bool = False
    script_args: dict = field(default_factory=dict)
    schedule: str | None = None
    job_type: GlueJobType = GlueJobType.GLUE_ETL


@dataclass
class GlueComponentArgs:
    """
    Glue job definitions and infrastructure dependencies such as IAM roles, external connections, code and data storage.

    :param jobs: the list of GlueJobDefinition to deploy
    :param execution_role: the IAM role attached to the Glue jobs if it exists, if not one will be createdw
    :param database_name: name of the Glue database if it exists, if not one will be created
    :param code_repository_bucket_name: name of the s3 code repository database if it exists, if not one will be created
    :param data_bucket_name: name of the s3 bucket to store data, if it exists, if not one will be created
    :param kafka_checkpoints_bucket_name: name of the s3 bucket to store checkpoints if it exists, if not one will be created
    :param connector_config: Connector configuration to run the Glue Jobs in a VPC.
    """

    jobs: list[GlueJobDefinition]
    execution_role: str = None
    database_name: str = None
    code_repository_bucket_name: str = None
    data_bucket_name: str = None
    kafka_checkpoints_bucket_name: str = None
    connector_config: Optional[ConnectorConfig] = None


class GlueComponent(PulumiComponentResource):
    """
    An opinionated deployment of a fully functional PySpark applications on Glue.

    Resources deployed:
    - Code Repository: s3 bucket
    - Data Storage: s3 bucket
    - Kafka checkpoint storage: s3 bucket
    - Compute: Glue Jobs
    - Orchestration: Triggers for the Glue Jobs
    - Metadata Catalog: Glue Database
    - Permissions: IAM role for Glue Jobs
        - Full access to S3 bucket with data
        - Full access to tables in Glue database
    """

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
        self.code_repository_bucket
        self.iceberg_database
        self.iceberg_bucket
        self.kafka_checkpoint_bucket
        self.connection
        self.jobs

    # Compute
    @property
    @cache
    def jobs(self) -> list[aws.glue.Job]:
        """
        Return all the Glue jobs for the application. Add a trigger for the job if a schedule is specified.
        """
        jobs = []
        for job in self.args.jobs:
            glue_job = aws.glue.Job(
                resource_name=f"{self._name}-{job.name}-job",
                opts=ResourceOptions(parent=self),
                name=self._get_job_name(job),
                glue_version=job.glue_version,
                role_arn=self.role.arn,
                command=aws.glue.JobCommandArgs(
                    name=job.job_type.value,
                    python_version="3",
                    script_location=self._get_source_path(job),
                ),
                default_arguments=self._get_default_arguments(job),
                number_of_workers=job.number_of_workers,
                worker_type=job.worker_type.value,
                execution_property=aws.glue.JobExecutionPropertyArgs(
                    max_concurrent_runs=job.max_concurrent_runs
                ),
                connections=[self.connection.name] if self.connection else [],
            )
            jobs.append(glue_job)
            if job.schedule:
                self._create_glue_trigger(job)
        return jobs

    def _get_job_name(self, job: GlueJobDefinition):
        return f"{self._name}-{job.name}-job"

    def _get_source_path(self, job: GlueJobDefinition) -> str:
        return (
            f"s3://{self.code_repository_bucket}/{job.script_location}"
            if job.script_location
            else f"s3://{self.code_repository_bucket}/{job.name}.py"
        )

    @staticmethod
    def _get_default_arguments(job: GlueJobDefinition) -> dict[str, str]:
        """The map of default arguments for this job.
        These are arguments that your own script consumes, as well as arguments that AWS Glue itself consumes.

        TODO: Handling of logging via log4j config file.
            - At Brenntag we found out how expensive Glue logging can become
            - An effective way to limit logging volume is by using a custom log4j configuration file
            - File needs to be uploaded to s3 and passed via
        """
        return {
            "--additional-python-modules": ",".join(job.extra_libraries),
            "--enable-auto-scaling": "true" if job.enable_auto_scaling else "false",
            "--enable-continuous-cloudwatch-log": (
                "true" if job.enable_continuous_cloudwatch_log else "false"
            ),
            "--enable-continuous-log-filter": (
                "true" if job.enable_continuous_log_filter else "false"
            ),
            "--enable-glue-datacatalog": (
                "true" if job.enable_continuous_log_filter else "false"
            ),
            "--datalake-formats": "iceberg",
            "--enable-metrics": "true" if job.enable_metrics else "false",
            "--enable-observability-metrics": (
                "true" if job.enable_observability_metrics else "false"
            ),
            **job.script_args,
        }

    @property
    @cache
    def role(self) -> aws.iam.Role:
        """Return an execution role for Glue jobs."""
        if self.args.execution_role:
            return aws.iam.Role.get(f"{self._name}-role", id=self.args.execution_role)

        return aws.iam.Role(
            resource_name=f"{self._name}-role",
            opts=ResourceOptions(parent=self),
            name=f"{self._name}-role",
            assume_role_policy=json.dumps(self.assume_policy),
            managed_policy_arns=self.managed_policy_arns,
        )

    # Permissions
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
        ]

    # Code Repository
    @property
    @cache
    def code_repository_bucket(self) -> aws.s3.BucketV2:
        """Return an S3 bucket for Glue jobs to host source codes.

        NOTE: using `bucket_prefix` to avoid name conflict as the bucket name must be globally unique.
        """
        if self.args.code_repository_bucket_name:
            return aws.s3.BucketV2.get(
                f"{self._name}-code-bucket", id=self.args.code_repository_bucket_name
            )

        return self.args.code_repository_bucket_name or aws.s3.BucketV2(
            resource_name=f"{self._name}-code-bucket",
            opts=ResourceOptions(parent=self),
            bucket_prefix=f"{self._name}-code-bucket",
        )

    # Data Storage
    @property
    @cache
    def iceberg_bucket(self) -> aws.s3.BucketV2:
        """Return an S3 bucket for Iceberg tables to store data processed by Glue jobs.

        NOTE: using `bucket_prefix` to avoid name conflict as the bucket name must be globally unique.
        """
        if self.args.data_bucket_name:
            return aws.s3.BucketV.get(
                f"{self._name}-data-bucket", id=self.args.data_bucket_name
            )

        return aws.s3.BucketV2(
            resource_name=f"{self._name}-data-bucket",
            opts=ResourceOptions(parent=self),
            bucket_prefix=f"{self._name}-data-bucket",
        )

    # Metadata
    @property
    @cache
    def iceberg_database(self) -> aws.glue.CatalogDatabase:
        """Return a Glue database for Iceberg tables to store data processed by Glue jobs."""
        if self.args.database_name:
            return aws.cloudwatch.CatalogDatabase.get(
                f"{self._name}-database", id=self.args.database_name
            )

        return aws.glue.CatalogDatabase(
            resource_name=f"{self._name}-database",
            opts=ResourceOptions(parent=self),
            name=f"{self._name}-database",
            location_uri=f"s3://{self.iceberg_bucket.bucket}/",
        )

    # Orchestration
    def _create_glue_trigger(
        self, job: GlueJobDefinition
    ) -> Optional[aws.glue.Trigger]:
        """Return a Glue Trigger object."""
        return (
            aws.glue.Trigger(
                f"{job.name}-glue-trigger",
                type="SCHEDULED",
                schedule=job.schedule,
                actions=[
                    aws.glue.TriggerActionArgs(
                        job_name=self._get_job_name(job),
                    )
                ],
                start_on_creation=True,
            )
            if job.schedule
            else None
        )

    # Kafka
    @property
    @cache
    def kafka_checkpoint_bucket(self) -> Optional[aws.s3.BucketV2]:
        """Return a s3 bucket to store the checkpoints.

        Creates the bucket if at least one job is of type 'gluestreaming'.
        """
        if "gluestreaming" in [job.job_type for job in self.args.jobs]:
            if self.args.kafka_checkpoints_bucket_name:
                return aws.s3.BucketV2.get(
                    f"{self._name}-checkpoints-bucket",
                    id=self.args.kafka_checkpoints_bucket_name,
                )

        return aws.s3.BucketV2(
            resource_name=f"{self._name}-checkpoints-bucket",
            opts=ResourceOptions(parent=self),
            bucket_prefix=f"{self._name}-checkpoints-bucket",
        )

    @property
    @cache
    def connection(self) -> Optional[aws.glue.Connection]:
        """Return a s3 bucket to store the checkpoints.

        Creates the bucket if at least one job is of type 'gluestreaming'.
        """
        if not self.args.connector_config:
            logging.warning(
                "No connector config provided. Glue jobs will run outside a VPC. This is not recommended."
            )
            return None

        return aws.glue.Connection(
            resource_name=f"{self._name}-kafka-connection",
            name=f"{self._name}-kafka-connection",
            connection_type=self.args.connector_config.connector_type.value,
            connection_properties=self.args.connector_config.connection_properties,
            physical_connection_requirements={
                "security_group_id_lists": self.args.connector_config.security_groups,
                "subnet_id": self.args.connector_config.subnet_id,
            },
        )
