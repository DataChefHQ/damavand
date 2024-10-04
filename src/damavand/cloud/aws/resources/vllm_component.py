import json
from typing import Any, Optional
from functools import cache
from dataclasses import dataclass

from sagemaker import image_uris
import pulumi
import pulumi_aws as aws
from pulumi import ComponentResource as PulumiComponentResource
from pulumi import ResourceOptions


@dataclass
class AwsVllmComponentArgs:
    """
    Arguments for the AwsVllmComponent component.

    ...

    Attributes
    ----------
    region : str
        region where the SageMaker model is going to be deployed.
    model_image_version : str
        version of the djl-lmi image.
    model_name : str
        name of the SageMaker model.
    instance_initial_count : int
        number of instances to deploy the model.
    instance_type : str
        type of instance to deploy the model.
    public_internet_access : bool
        whether to deploy a public API for the model.
    api_env_name : str
        the name of the API environment.
    cognito_user_pool_id : Optional[str]
        the Cognito user pool ID for authentication.
    """

    region: str = "us-west-2"
    model_image_version: str = "0.29.0"
    model_name: str = "microsoft/Phi-3-mini-4k-instruct"
    instance_initial_count: int = 1
    instance_type: str = "ml.g4dn.xlarge"
    public_internet_access: bool = False
    api_env_name: str = "prod"
    cognito_user_pool_id: Optional[str] = None


class AwsVllmComponent(PulumiComponentResource):
    """
    The AwsVllmComponent class is a Pulumi component that deploys an LLM model using vLLM.

    ...

    Attributes
    ----------
    name : str
        the name of the component.
    args : AwsVllmComponentArgs
        the arguments of the component.
    opts : Optional[ResourceOptions]
        the resource options.

    Methods
    -------
    assume_policy()
        Return the assume role policy for SageMaker.
    managed_policy_arns()
        Return a list of managed policy ARNs that defines the permissions for Sagemaker.
    role()
        Return an execution role for SageMaker.
    model_image_ecr_path()
        Return the ECR image path for the djl-lmi container image serving vllm.
    model_image_configs()
        Return the environment configurations for the vllm image.
    model()
        Return a SageMaker model.
    endpoint_config()
        Return a SageMaker endpoint configuration for the vllm model.
    endpoint()
        Return a SageMaker endpoint for the vllm model.
    """

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

        print(">>>> self.args: ", self.args)
        _ = self.model
        _ = self.endpoint_config
        _ = self.endpoint

        _ = self.api
        _ = self.api_resource

        if not self.args.public_internet_access:
            _ = self.api_authorizer

        _ = self.api_method
        _ = self.api_integration
        _ = self.api_integration_response
        _ = self.api_method_response
        _ = self.api_deploy


    def get_service_assume_policy(self, service: str) -> dict[str, Any]:
        """Return the assume role policy for the requested service.

        Parameters
        ----------
        service : str
            the service url that can assume the role.

        Returns
        -------
        dict[str, Any]
            the assume role policy.
        """

        return {
            "Version": "2012-10-17",
            "Statement": [
                {
                    "Effect": "Allow",
                    "Principal": {
                        "Service": service,
                    },
                    "Action": "sts:AssumeRole",
                },
            ],
        }

    @property
    def sagemaker_access_policies(self) -> list[str]:
        """Return a list of managed policy ARNs that defines the permissions for Sagemaker."""

        return [
            aws.iam.ManagedPolicy.AMAZON_SAGE_MAKER_FULL_ACCESS,
            aws.iam.ManagedPolicy.AMAZON_S3_FULL_ACCESS,
            aws.iam.ManagedPolicy.CLOUD_WATCH_FULL_ACCESS_V2,
        ]

    @property
    @cache
    def sagemaker_execution_role(self) -> aws.iam.Role:
        """Return an execution role for Glue jobs."""

        return aws.iam.Role(
            resource_name=f"{self._name}-role",
            opts=ResourceOptions(parent=self),
            name=f"{self._name}-ExecutionRole",
            assume_role_policy=json.dumps(
                self.get_service_assume_policy("sagemaker.amazonaws.com")
            ),
            managed_policy_arns=self.sagemaker_access_policies,
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
            execution_role_arn=self.sagemaker_execution_role.arn,
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

    @property
    @cache
    def api(self) -> aws.apigateway.RestApi:
        """
        Return a public API for the SageMaker endpoint.

        """

        return aws.apigateway.RestApi(
            resource_name=f"{self._name}-api",
            opts=ResourceOptions(parent=self),
            endpoint_configuration=aws.apigateway.RestApiEndpointConfigurationArgs(
                types="REGIONAL",
            ),
        )

    @property
    @cache
    def api_resource(self) -> aws.apigateway.Resource:
        """
        Return a resource for the API Gateway.

        """

        return aws.apigateway.Resource(
            resource_name=f"{self._name}-api-resource",
            opts=ResourceOptions(parent=self),
            rest_api=self.api.id,
            parent_id=self.api.root_resource_id,
            path_part="completions",
        )

    @property
    @cache
    def api_authorizer(self) -> aws.apigateway.Authorizer:
        """
        Return an authorizer for the API Gateway.

        Raises
        ------
        AttributeError
            When public_internet_access is True.

        AttributeError
            When cognito_user_pool_id is not set.
        """

        if self.args.public_internet_access:
            raise AttributeError(
                "`api_authorizer`is only available when public_internet_access is False"
            )

        if not self.args.cognito_user_pool_id:
            raise AttributeError(
                "`api_authorizer` requires a cognito_user_pool_id to be set"
            )


        return aws.apigateway.Authorizer(
            resource_name=f"{self._name}-api-authorizer",
            opts=ResourceOptions(parent=self),
            rest_api=self.api.id,
            type="COGNITO_USER_POOLS",
            provider_arns=[self.args.cognito_user_pool_id],
        )

    @property
    @cache
    def api_method(self) -> aws.apigateway.Method:
        """
        Return a method for the API Gateway.

        """

        if self.args.public_internet_access:
            return aws.apigateway.Method(
                resource_name=f"{self._name}-api-method",
                opts=ResourceOptions(parent=self),
                rest_api=self.api.id,
                resource_id=self.api_resource.id,
                http_method="POST",
                authorization="NONE",
            )
        else:
            return aws.apigateway.Method(
                resource_name=f"{self._name}-api-method",
                opts=ResourceOptions(parent=self),
                rest_api=self.api.id,
                resource_id=self.api_resource.id,
                http_method="POST",
                authorization="COGNITO_USER_POOLS",
                authorizer_id=self.api_authorizer.id,
            )

    @property
    def api_sagemaker_integration_uri(self) -> pulumi.Output[str]:
        """
        Return the SageMaker model integration URI for the API Gateway

        """

        return self.endpoint.name.apply(
            lambda name: f"arn:aws:apigateway:{self.args.region}:runtime.sagemaker:path/endpoints/{name}/invocations"
        )

    @property
    def apigateway_access_policies(self) -> list[str]:
        """Return a list of managed policy ARNs that defines the permissions for APIGateway."""

        return [
            aws.iam.ManagedPolicy.AMAZON_SAGE_MAKER_FULL_ACCESS,
        ]

    @property
    @cache
    def api_access_sagemaker_role(self) -> aws.iam.Role:
        """
        Return an execution role for APIGateway to access SageMaker endpoints.

        """

        return aws.iam.Role(
            resource_name=f"{self._name}-api-sagemaker-access-role",
            opts=ResourceOptions(parent=self),
            assume_role_policy=json.dumps(
                self.get_service_assume_policy("apigateway.amazonaws.com")
            ),
            managed_policy_arns=self.apigateway_access_policies,
        )

    @property
    @cache
    def api_integration(self) -> aws.apigateway.Integration:
        """
        Return a sagemaker integration for the API Gateway.

        """

        return aws.apigateway.Integration(
            resource_name=f"{self._name}-api-integration",
            opts=ResourceOptions(parent=self),
            rest_api=self.api.id,
            resource_id=self.api_resource.id,
            http_method=self.api_method.http_method,
            integration_http_method="POST",
            type="AWS",
            uri=self.api_sagemaker_integration_uri,
            credentials=self.api_access_sagemaker_role.arn,
        )

    @property
    @cache
    def api_integration_response(self) -> aws.apigateway.IntegrationResponse:
        """
        Return a sagemaker integration response for the API Gateway.

        """

        return aws.apigateway.IntegrationResponse(
            resource_name=f"{self._name}-api-integration-response",
            opts=ResourceOptions(parent=self, depends_on=[self.api_integration]),
            rest_api=self.api.id,
            resource_id=self.api_resource.id,
            http_method=self.api_method.http_method,
            status_code="200",
        )

    @property
    @cache
    def api_method_response(self) -> aws.apigateway.MethodResponse:
        """
        Return a sagemaker method response for the API Gateway.

        """

        return aws.apigateway.MethodResponse(
            resource_name=f"{self._name}-api-method-response",
            opts=ResourceOptions(parent=self),
            rest_api=self.api.id,
            resource_id=self.api_resource.id,
            http_method="POST",
            status_code="200",
        )

    @property
    @cache
    def api_deploy(self) -> aws.apigateway.Deployment:
        """
        Return an API deployment for the API Gateway.

        """

        return aws.apigateway.Deployment(
            resource_name=f"{self._name}-api-deploy",
            opts=ResourceOptions(
                parent=self,
                depends_on=[
                    self.api_method_response,
                    self.api_integration_response,
                    self.api_integration,
                ],
            ),
            rest_api=self.api.id,
            stage_name=self.args.api_env_name,
        )
