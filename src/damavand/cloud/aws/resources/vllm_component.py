import json
from typing import Any, Optional
from functools import cache
from dataclasses import dataclass

from sagemaker import image_uris
import pulumi_aws as aws
from pulumi import ComponentResource as PulumiComponentResource
from pulumi import ResourceOptions


@dataclass
class AwsVllmComponentArgs:
    region: str = "us-west-2"
    model_image_version: str = "0.29.0"
    model_name = "microsoft/Phi-3-mini-4k-instruct"
    instance_initial_count = 1
    instance_type = "ml.g4dn.xlarge"


class AwsVllmComponent(PulumiComponentResource):
    def __init__(
        self,
        name: str,
        args: AwsVllmComponentArgs,
        opts: Optional[ResourceOptions] = None,
    ) -> None:
        super().__init__(
            f"Damavand:{AwsVllmComponent.__name__}",
            name=name,
            props={},
            opts=opts,
            remote=False,
        )

        self.args = args
        _ = self.model

    @property
    def assume_policy(self) -> dict[str, Any]:
        """Return the assume role policy for SageMaker."""

        return {
            "Version": "2012-10-17",
            "Statement": [
                {
                    "Effect": "Allow",
                    "Principal": {
                        "Service": "sagemaker.amazonaws.com",
                    },
                    "Action": "sts:AssumeRole",
                },
            ],
        }

    @property
    def managed_policy_arns(self) -> list[str]:
        """Return a list of managed policy ARNs that defines the permissions for Sagemaker."""

        return [
            aws.iam.ManagedPolicy.AMAZON_SAGE_MAKER_FULL_ACCESS,
            aws.iam.ManagedPolicy.AMAZON_S3_FULL_ACCESS,
            aws.iam.ManagedPolicy.CLOUD_WATCH_FULL_ACCESS_V2,
        ]

    @property
    @cache
    def role(self) -> aws.iam.Role:
        """Return an execution role for Glue jobs."""

        return aws.iam.Role(
            resource_name=f"{self._name}-role",
            opts=ResourceOptions(parent=self),
            name=f"{self._name}-ExecutionRole",
            assume_role_policy=json.dumps(self.assume_policy),
            managed_policy_arns=self.managed_policy_arns,
        )

    @property
    @cache
    def model_image_ecr_path(self) -> str:
        """Return the ECR image path for the vLLM model."""

        return image_uris.retrieve(
            framework="djl-lmi",
            version=self.args.model_image_version,
            region=self.args.region,
        )

    @property
    @cache
    def model_image_configs(self) -> dict[str, str]:
        """Return the environment configurations for the vLLM image."""

        return {
            "HF_MODEL_ID": self.args.model_name,
            "OPTION_ROLLING_BATCH": "vllm",
            "TENSOR_PARALLEL_DEGREE": "max",
            "OPTION_MAX_ROLLING_BATCH_SIZE": "2",
            "OPTION_DTYPE": "fp16",
        }

    @property
    @cache
    def model(self) -> aws.sagemaker.Model:
        """Return a SageMaker model."""

        return aws.sagemaker.Model(
            resource_name=f"{self._name}-model",
            opts=ResourceOptions(parent=self),
            primary_container=aws.sagemaker.ModelPrimaryContainerArgs(
                image=self.model_image_ecr_path,
                environment=self.model_image_configs,
            ),
            execution_role_arn=self.role.arn,
        )

    @property
    @cache
    def endpoint_config(self) -> aws.sagemaker.EndpointConfiguration:
        """Return a SageMaker endpoint configuration for the vllm model."""

        return aws.sagemaker.EndpointConfiguration(
            resource_name=f"{self._name}-endpoint-config",
            opts=ResourceOptions(parent=self),
            production_variants=[
                aws.sagemaker.EndpointConfigurationProductionVariantArgs(
                    initial_instance_count=self.args.instance_initial_count,
                    initial_variant_weight=1,
                    instance_type=self.args.instance_type,
                    model_name=self.model.name,
                ),
            ],
        )

    @property
    @cache
    def endpoint(self) -> aws.sagemaker.Endpoint:
        """Return a SageMaker endpoint for the vllm model."""

        return aws.sagemaker.Endpoint(
            resource_name=f"{self._name}-endpoint",
            opts=ResourceOptions(parent=self),
            endpoint_config_name=self.endpoint_config.name,
        )
