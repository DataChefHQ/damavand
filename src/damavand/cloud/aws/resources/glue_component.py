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
    """Enum representing Glue worker types."""

    G_1X = "G.1X"
    G_2X = "G.2X"
    G_4X = "G.4X"
    G_8X = "G.8X"
    G_025X = "G.025X"
    Z_2X = "Z.2X"


class GlueJobType(Enum):
    """Enum representing Glue job types."""

    ETL = "glueetl"
    STREAMING = "gluestreaming"


class GlueExecutionClass(Enum):
    """Enum representing Glue execution classes."""

    STANDARD = "STANDARD"
    FLEX = "FLEX"


class ConnectionType(Enum):
    """Enum representing connection types."""

    KAFKA = "KAFKA"


@dataclass
class ConnectorConfig:
    """Configuration for the Connector.

    Attributes:
        vpc_id (str): VPC ID.
        subnet_id (str): Subnet ID.
        security_groups (list[str]): List of security group IDs.
        connector_type (ConnectionType): Connector type. Default is ConnectionType.KAFKA.
        connection_properties (dict): Connection properties. Default is empty dict.
    """

    vpc_id: str
    subnet_id: str
    security_groups: list[str]
    connector_type: ConnectionType = ConnectionType.KAFKA
    connection_properties: dict = field(default_factory=dict)


@dataclass
class GlueJobDefinition:
    """Parameters for the Glue job.

    Attributes:
        name (str): Job name.
        description (str): Job description.
        script_location (str): S3 path to the entrypoint script.
        extra_libraries (list[str]): Paths to extra dependencies.
        execution_class (GlueExecutionClass): Execution class. Default is STANDARD.
        max_concurrent_runs (int): Max concurrent runs.
        glue_version (str): Glue version.
        enable_auto_scaling (bool): Enable auto-scaling.
        max_capacity (int): Max capacity.
        max_retries (int): Max retries.
        number_of_workers (int): Number of workers.
        timeout (int): Job timeout in minutes.
        worker_type (GlueWorkerType): Worker type.
        enable_glue_datacatalog (bool): Use Glue Data Catalog.
        enable_continuous_cloudwatch_log (bool): Enable continuous CloudWatch log.
        enable_continuous_log_filter (bool): Reduce logging amount.
        enable_metrics (bool): Enable metrics.
        enable_observability_metrics (bool): Enable extra Spark metrics.
        script_args (dict): Script arguments.
        schedule (Optional[str]): Cron-like schedule.
        job_type (GlueJobType): Job type.
    """

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
    timeout: int = 2880
    worker_type: GlueWorkerType = GlueWorkerType.G_1X
    enable_glue_datacatalog: bool = True
    enable_continuous_cloudwatch_log: bool = False
    enable_continuous_log_filter: bool = True
    enable_metrics: bool = False
    enable_observability_metrics: bool = False
    script_args: dict = field(default_factory=dict)
    schedule: Optional[str] = None
    job_type: GlueJobType = GlueJobType.ETL


@dataclass
class GlueComponentArgs:
    """Glue job definitions and infrastructure dependencies.

    Attributes:
        jobs (list[GlueJobDefinition]): List of Glue jobs to deploy.
        execution_role (Optional[str]): IAM role for Glue jobs.
        connector_config (Optional[ConnectorConfig]): Connector configuration.
    """

    jobs: list[GlueJobDefinition]
    execution_role: Optional[str] = None
    connector_config: Optional[ConnectorConfig] = None


class GlueComponent(PulumiComponentResource):
    """Deployment of PySpark applications on Glue.

    Resources deployed:
        - Code Repository: S3 bucket.
        - Data Storage: S3 bucket.
        - Kafka checkpoint storage: S3 bucket.
        - Compute: Glue Jobs.
        - Orchestration: Triggers for the Glue Jobs.
        - Metadata Catalog: Glue Database.
        - Permissions: IAM role for Glue Jobs.

    Args:
        name (str): The name of the resource.
        args (GlueComponentArgs): The arguments for the component.
        opts (Optional[ResourceOptions]): Resource options.
    """

    def __init__(
        self,
        name: str,
        tags: dict[str, str],
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
        self.jobs

        if any(job.job_type == GlueJobType.STREAMING for job in self.args.jobs):
            self.kafka_checkpoint_bucket

        if not self.args.connector_config:
            logging.warning(
                "No connector config provided. Glue jobs will run outside a VPC."
            )
        else:
            self.connection

    @property
    @cache
    def jobs(self) -> list[aws.glue.Job]:
        """Creates and returns all the Glue jobs and adds triggers if scheduled.

        Returns:
            list[aws.glue.Job]: List of Glue jobs.
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
                connections=(
                    [self.connection.name] if self.args.connector_config else []
                ),
            )
            jobs.append(glue_job)
            if job.schedule:
                self._create_glue_trigger(job)
        return jobs

    def _get_job_name(self, job: GlueJobDefinition) -> str:
        """Generates the job name.

        Args:
            job (GlueJobDefinition): The job definition.

        Returns:
            str: The job name.
        """
        return f"{self._name}-{job.name}-job"

    def _get_source_path(self, job: GlueJobDefinition) -> str:
        """Gets the source path for the job script.

        Args:
            job (GlueJobDefinition): The job definition.

        Returns:
            str: The S3 path to the job script.
        """
        return (
            f"s3://{self.code_repository_bucket.bucket}/{job.script_location}"
            if job.script_location
            else f"s3://{self.code_repository_bucket.bucket}/{job.name}.py"
        )

    def _get_default_arguments(self, job: GlueJobDefinition) -> dict[str, str]:
        """Returns the map of default arguments for this job.

        Args:
            job (GlueJobDefinition): The job definition.

        Returns:
            dict[str, str]: The default arguments for the job.
        """
        return {
            "--additional-python-modules": ",".join(job.extra_libraries),
            "--enable-auto-scaling": str(job.enable_auto_scaling).lower(),
            "--enable-continuous-cloudwatch-log": str(
                job.enable_continuous_cloudwatch_log
            ).lower(),
            "--enable-continuous-log-filter": str(
                job.enable_continuous_log_filter
            ).lower(),
            "--enable-glue-datacatalog": str(job.enable_glue_datacatalog).lower(),
            "--datalake-formats": "iceberg",
            "--enable-metrics": str(job.enable_metrics).lower(),
            "--enable-observability-metrics": str(
                job.enable_observability_metrics
            ).lower(),
            **job.script_args,
        }

    @property
    @cache
    def role(self) -> aws.iam.Role:
        """Returns an execution role for Glue jobs.

        Returns:
            aws.iam.Role: The IAM role for Glue jobs.
        """
        if self.args.execution_role:
            return aws.iam.Role.get(f"{self._name}-role", id=self.args.execution_role)

        return aws.iam.Role(
            resource_name=f"{self._name}-role",
            opts=ResourceOptions(parent=self),
            name=f"{self._name}-role",
            assume_role_policy=json.dumps(self.assume_policy),
            managed_policy_arns=self.managed_policy_arns,
        )

    @property
    def assume_policy(self) -> dict[str, Any]:
        """Returns the assume role policy for Glue jobs.

        Returns:
            dict[str, Any]: The assume role policy.
        """
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
        """Returns the managed policy ARNs defining permissions for Glue jobs.

        Returns:
            list[str]: List of managed policy ARNs.
        """
        return [
            aws.iam.ManagedPolicy.AWS_GLUE_SERVICE_ROLE,
            aws.iam.ManagedPolicy.AMAZON_S3_FULL_ACCESS,
        ]

    @property
    @cache
    def code_repository_bucket(self) -> aws.s3.BucketV2:
        """Returns an S3 bucket for Glue jobs to host source codes.

        Returns:
            aws.s3.BucketV2: The S3 bucket for code repository.
        """
        return aws.s3.BucketV2(
            resource_name=f"{self._name}-code-bucket",
            opts=ResourceOptions(parent=self),
            bucket_prefix=f"{self._name[:20]}-code-bucket",
        )

    @property
    @cache
    def iceberg_bucket(self) -> aws.s3.BucketV2:
        """Returns an S3 bucket for Iceberg tables to store data.

        Returns:
            aws.s3.BucketV2: The S3 bucket for Iceberg data.
        """
        return aws.s3.BucketV2(
            resource_name=f"{self._name}-data-bucket",
            opts=ResourceOptions(parent=self),
            bucket_prefix=f"{self._name[:20]}-data-bucket",
        )

    @property
    @cache
    def iceberg_database(self) -> aws.glue.CatalogDatabase:
        """Returns a Glue database for Iceberg tables.

        Returns:
            aws.glue.CatalogDatabase: The Glue database.
        """
        return aws.glue.CatalogDatabase(
            resource_name=f"{self._name}-database",
            opts=ResourceOptions(parent=self),
            name=f"{self._name[:20]}-database",
            location_uri=f"s3://{self.iceberg_bucket.bucket}/",
        )

    def _create_glue_trigger(self, job: GlueJobDefinition) -> aws.glue.Trigger:
        """Creates a Glue Trigger for the job if scheduled.

        Args:
            job (GlueJobDefinition): The job definition.

        Returns:
            aws.glue.Trigger: The Glue trigger.
        """
        return aws.glue.Trigger(
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

    @property
    @cache
    def kafka_checkpoint_bucket(self) -> aws.s3.BucketV2:
        """Returns an S3 bucket to store Kafka checkpoints.

        Returns:
            aws.s3.BucketV2: The S3 bucket for Kafka checkpoints.
        """
        return aws.s3.BucketV2(
            resource_name=f"{self._name}-checkpoints-bucket",
            opts=ResourceOptions(parent=self),
            bucket_prefix=f"{self._name[:20]}-checkpoints-bucket",
        )

    @property
    @cache
    def connection(self) -> aws.glue.Connection:
        """Returns a Glue Connection.

        Returns:
            aws.glue.Connection: The Glue Connection.
        """
        if not self.args.connector_config:
            raise ValueError("No connector config provided.")

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
