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
    api_key_required : bool
        whether an API key is required for interacting with the API.
    api_key_secret_name : Optional[str]
        the name of the Secret Manager secret to store the API key.
    api_env_name : str
        the name of the API environment.
    endpoint_ssm_parameter_name : str
        the name of the SSM parameter to store the endpoint URL.
    """

    region: str = "us-west-2"
    model_image_version: str = "0.29.0"
    model_name: str = "microsoft/Phi-3-mini-4k-instruct"
    instance_initial_count: int = 1
    instance_type: str = "ml.g4dn.xlarge"
    api_key_required: bool = True
    api_env_name: str = "prod"
    api_key_ssm_name: Optional[str] = None
    endpoint_ssm_parameter_name: str = "/Vllm/endpoint/url"


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
    get_service_assume_policy(service)
        Return the assume role policy for the requested service.
    sagemaker_access_policies()
        Return a list of managed policy ARNs that defines the permissions for Sagemaker.
    sagemaker_execution_role()
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
    api()
        Return a public APIGateway RESTAPI for the SageMaker endpoint.
    api_resource_v1()
        Return a resource for API version routing.
    api_resource_chat()
        Return a resource for chat routing.
    api_resource_completions()
        Return a resource for completions routing.
    api_method()
        Return openai chat completions compatible method.
    admin_api_key()
        Return an admin API key for the API Gateway.
    api_key_secret()
        Return the Secret Manager secret for storing the API key.
    api_key_secret_version()
        Return the Secret Manager secret version (value) for storing the API key.
    default_usage_plan()
        Return a default usage plan for the API Gateway.
    tier_1_usage_plan()
        Return a tier 1 usage plan for the API Gateway.
    tier_2_usage_plan()
        Return a tier 2 usage plan for the API Gateway.
    tier_3_usage_plan()
        Return a tier 3 usage plan for the API Gateway.
    api_key_usage_plan()
        Return the UsagePlanKey where the default usage plan is associated with the API and admin API key.
    api_sagemaker_integration_uri()
        Return the SageMaker model integration URI for the API Gateway.
    apigateway_access_policies()
        Return a list of managed policy ARNs that defines the permissions for APIGateway.
    api_access_sagemaker_role()
        Return an execution role for APIGateway to access SageMaker endpoints.
    api_integration()
        Return a sagemaker integration for the API Gateway.
    api_integration_response()
        Return a sagemaker integration response for the API Gateway.
    api_method_response()
        Return a sagemaker method response for the API Gateway.
    api_deployment()
        Return an API deployment for the API Gateway.
    endpoint_base_url()
        Return the base URL for the deployed endpoint.
    endpoint_ssm_parameter()
        Return an SSM parameter that stores the deployed endpoint URL.
    """

    def __init__(
        self,
        name: str,
        tags: dict[str, str],
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
        self._tags = tags

        _ = self.model
        _ = self.endpoint_config
        _ = self.endpoint

        _ = self.api
        _ = self.api_resource_v1
        _ = self.api_resource_chat
        _ = self.api_resource_completions

        # Only create API key if public internet access is set to False
        if self.args.api_key_required:
            _ = self.admin_api_key
            _ = self.default_usage_plan
            _ = self.tier_1_usage_plan
            _ = self.tier_2_usage_plan
            _ = self.tier_3_usage_plan
            _ = self.api_key_usage_plan
            _ = self.api_key_secret
            _ = self.api_key_secret_version
            _ = self.api_key_secret_ssm

        _ = self.api_method
        _ = self.api_integration
        _ = self.api_integration_response
        _ = self.api_method_response
        _ = self.api_deployment
        _ = self.endpoint_ssm_parameter

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
            tags=self._tags,
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
            tags=self._tags,
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
            tags=self._tags,
        )

    @property
    @cache
    def endpoint(self) -> aws.sagemaker.Endpoint:
        """Return a SageMaker endpoint for the vllm model."""

        return aws.sagemaker.Endpoint(
            resource_name=f"{self._name}-endpoint",
            opts=ResourceOptions(parent=self),
            endpoint_config_name=self.endpoint_config.name,
            tags=self._tags,
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
            tags=self._tags,
        )

    @property
    @cache
    def api_resource_v1(self) -> aws.apigateway.Resource:
        """
        Return a resource for the API Gateway.

        """

        return aws.apigateway.Resource(
            resource_name=f"{self._name}-api-resource-v1",
            opts=ResourceOptions(parent=self),
            rest_api=self.api.id,
            parent_id=self.api.root_resource_id,
            path_part="v1",
        )

    @property
    @cache
    def api_resource_chat(self) -> aws.apigateway.Resource:
        """
        Return a resource for the API Gateway.

        Raises
        ------
        AttributeError
            When api_key_required is False.
        """

        return aws.apigateway.Resource(
            resource_name=f"{self._name}-api-resource-chat",
            opts=ResourceOptions(parent=self),
            rest_api=self.api.id,
            parent_id=self.api_resource_v1.id,
            path_part="chat",
        )

    @property
    @cache
    def api_resource_completions(self) -> aws.apigateway.Resource:
        """
        Return a resource for the API Gateway.
        """

        return aws.apigateway.Resource(
            resource_name=f"{self._name}-api-resource-completions",
            opts=ResourceOptions(parent=self),
            rest_api=self.api.id,
            parent_id=self.api_resource_chat.id,
            path_part="completions",
        )

    @property
    @cache
    def api_method(self) -> aws.apigateway.Method:
        """
        Return a method for the API Gateway.
        """

        return aws.apigateway.Method(
            resource_name=f"{self._name}-api-method",
            opts=ResourceOptions(parent=self),
            rest_api=self.api.id,
            resource_id=self.api_resource_completions.id,
            http_method="POST",
            authorization="NONE",
            api_key_required=self.args.api_key_required,
        )

    @property
    @cache
    def admin_api_key(self) -> aws.apigateway.ApiKey:
        """
        Return the admin API key for the API Gateway


        Raises
        ------
        AttributeError
            When api_key_required is False.
        """
        if not self.args.api_key_required:
            raise AttributeError(
                "`admin_api_key` is only available when api_key_required is False"
            )

        return aws.apigateway.ApiKey(
            resource_name=f"{self._name}-api-key",
            opts=ResourceOptions(parent=self),
            tags=self._tags,
        )

    @property
    @cache
    def api_key_secret(self) -> aws.secretsmanager.Secret:
        """
        Return the secret for the API key


        Raises
        ------
        AttributeError
            When api_key_required is False.
        """
        if not self.args.api_key_required:
            raise AttributeError(
                "`api_key_secret` is only available when api_key_required is False"
            )

        return aws.secretsmanager.Secret(
            resource_name=f"{self._name}-api-key-secret",
            opts=ResourceOptions(parent=self),
            name_prefix=f"{self._name}/api-key/default",
            tags=self._tags,
        )

    @property
    @cache
    def api_key_secret_ssm(self) -> aws.ssm.Parameter:
        """
        Return the SSM parameter for the API key secret

        Secret Manager secrets have a time to live before they are deleted. As a result, a new secret name is required if the secret needs to be recreated. The parameter store provides a unique reference to the secret.


        Raises
        ------
        AttributeError
            When api_key_required is False.
        """
        if not self.args.api_key_required:
            raise AttributeError(
                "`api_key_secret_ssm` is only available when api_key_required is False"
            )

        return aws.ssm.Parameter(
            resource_name=f"{self._name}-api-key-secret-ssm",
            opts=ResourceOptions(parent=self),
            name=self.args.api_key_ssm_name,
            type=aws.ssm.ParameterType.STRING,
            value=self.api_key_secret.name,
            tags=self._tags,
        )

    @property
    @cache
    def api_key_secret_version(self) -> aws.secretsmanager.SecretVersion:
        """
        Return the secret version for the API key

        Raises
        ------
        AttributeError
            When api_key_required is False.
        """
        if not self.args.api_key_required:
            raise AttributeError(
                "`api_key_secret_version` is only available when api_key_required is False"
            )

        return aws.secretsmanager.SecretVersion(
            resource_name=f"{self._name}-api-key-secret-version",
            opts=ResourceOptions(parent=self, depends_on=[self.api_key_secret]),
            secret_id=self.api_key_secret.id,
            secret_string=self.admin_api_key.value,
        )

    @property
    @cache
    def default_usage_plan(self) -> aws.apigateway.UsagePlan:
        """
        Return a default usage plan for the API Gateway, that does not limit the usage.

        Raises
        ------
        AttributeError
            When api_key_required is False.
        """
        if not self.args.api_key_required:
            raise AttributeError(
                "`default_usage_plan` is only available when api_key_required is False"
            )

        return aws.apigateway.UsagePlan(
            resource_name=f"{self._name}-default-api-usage-plan",
            opts=ResourceOptions(parent=self, depends_on=[self.api_deployment]),
            api_stages=[
                aws.apigateway.UsagePlanApiStageArgs(
                    api_id=self.api.id,
                    # NOTE: How do we want to deal with API stages vs. AWS environments?
                    stage=self.args.api_env_name,
                )
            ],
            tags=self._tags,
        )

    @property
    @cache
    def tier_1_usage_plan(self) -> aws.apigateway.UsagePlan:
        """
        Return a tier 1 usage plan for the API Gateway, with the following limits:
        - requests per minute: 500

        Raises
        ------
        AttributeError
            When api_key_required is False.
        """
        if not self.args.api_key_required:
            raise AttributeError(
                "`default_usage_plan` is only available when api_key_required is False"
            )

        return aws.apigateway.UsagePlan(
            resource_name=f"{self._name}-tier-1-api-usage-plan",
            opts=ResourceOptions(parent=self, depends_on=[self.api_deployment]),
            api_stages=[
                aws.apigateway.UsagePlanApiStageArgs(
                    api_id=self.api.id,
                    stage=self.args.api_env_name,
                )
            ],
            throttle_settings=aws.apigateway.UsagePlanThrottleSettingsArgs(
                rate_limit=500
            ),
            tags=self._tags,
        )

    @property
    @cache
    def tier_2_usage_plan(self) -> aws.apigateway.UsagePlan:
        """
        Return a tier 2 usage plan for the API Gateway, with the following limits:
        - requests per minute: 5000

        Raises
        ------
        AttributeError
            When api_key_required is False.
        """
        if not self.args.api_key_required:
            raise AttributeError(
                "`default_usage_plan` is only available when api_key_required is False"
            )

        return aws.apigateway.UsagePlan(
            resource_name=f"{self._name}-tier-2-api-usage-plan",
            opts=ResourceOptions(parent=self, depends_on=[self.api_deployment]),
            api_stages=[
                aws.apigateway.UsagePlanApiStageArgs(
                    api_id=self.api.id,
                    stage=self.args.api_env_name,
                )
            ],
            throttle_settings=aws.apigateway.UsagePlanThrottleSettingsArgs(
                rate_limit=5000
            ),
            tags=self._tags,
        )

    @property
    @cache
    def tier_3_usage_plan(self) -> aws.apigateway.UsagePlan:
        """
        Return a tier 3 usage plan for the API Gateway, with the following limits:
        - requests per minute: 10000

        Raises
        ------
        AttributeError
            When api_key_required is False.
        """
        if not self.args.api_key_required:
            raise AttributeError(
                "`default_usage_plan` is only available when api_key_required is False"
            )

        return aws.apigateway.UsagePlan(
            resource_name=f"{self._name}-tier-3-api-usage-plan",
            opts=ResourceOptions(parent=self, depends_on=[self.api_deployment]),
            api_stages=[
                aws.apigateway.UsagePlanApiStageArgs(
                    api_id=self.api.id,
                    stage=self.args.api_env_name,
                )
            ],
            throttle_settings=aws.apigateway.UsagePlanThrottleSettingsArgs(
                rate_limit=10000
            ),
            tags=self._tags,
        )

    @property
    @cache
    def api_key_usage_plan(self) -> aws.apigateway.UsagePlanKey:
        """
        Return the usage plan key for the API Gateway

        Raises
        ------
        AttributeError
            When api_key_required is False.
        """
        if not self.args.api_key_required:
            raise AttributeError(
                "`api_key_usage_plan` is only available when api_key_required is False"
            )

        return aws.apigateway.UsagePlanKey(
            resource_name=f"{self._name}-api-usage-plan-key",
            opts=ResourceOptions(parent=self),
            key_id=self.admin_api_key.id,
            key_type="API_KEY",
            usage_plan_id=self.default_usage_plan.id,
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
            tags=self._tags,
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
            resource_id=self.api_resource_completions.id,
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
            resource_id=self.api_resource_completions.id,
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
            resource_id=self.api_resource_completions.id,
            http_method=self.api_method.http_method,
            status_code="200",
        )

    @property
    @cache
    def api_deployment(self) -> aws.apigateway.Deployment:
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

    @property
    def endpoint_base_url(self) -> pulumi.Output[str]:
        """
        Return the base URL for the deployed endpoint.

        """

        return pulumi.Output.all(
            self.api_deployment.invoke_url, self.api_resource_v1.path_part
        ).apply(lambda args: f"{args[0]}/{args[1]}")

    @property
    @cache
    def endpoint_ssm_parameter(self) -> aws.ssm.Parameter:
        """
        Return an SSM parameter that stores the deployed endpoint URL.

        """

        return aws.ssm.Parameter(
            resource_name=f"{self._name}-endpoint-ssm-parameter",
            opts=ResourceOptions(parent=self),
            name=self.args.endpoint_ssm_parameter_name,
            type=aws.ssm.ParameterType.STRING,
            value=self.endpoint_base_url,
            tags=self._tags,
        )
