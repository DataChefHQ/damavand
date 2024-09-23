import pytest
from typing import Optional, Tuple, List

import pulumi
import pulumi_aws as aws
from pulumi.runtime.mocks import MockResourceArgs, MockCallArgs


# NOTE: this has to be defined before importing infrastructure codes.
# Check Pulumi's documentation for more details: https://www.pulumi.com/docs/using-pulumi/testing/unit/
class MyMocks(pulumi.runtime.Mocks):
    def new_resource(self, args: MockResourceArgs) -> Tuple[Optional[str], dict]:
        return (args.name + "_id", args.inputs)

    def call(self, args: MockCallArgs) -> Tuple[dict, Optional[List[Tuple[str, str]]]]:
        return ({}, None)


pulumi.runtime.set_mocks(
    MyMocks(),
    preview=False,  # Sets the flag `dry_run`, which is true at runtime during a preview.
)

from damavand.cloud.aws.resources import (  # noqa: E402
    AwsVllmComponent,
    AwsVllmComponentArgs,
)


def test_private_internet_access():
    vllm = AwsVllmComponent(
        name="test",
        args=AwsVllmComponentArgs(),
    )

    with pytest.raises(AttributeError):
        vllm.api
        vllm.api_resource
        vllm.api_method
        vllm.api_access_sagemaker_role
        vllm.api_integration
        vllm.api_integration_response
        vllm.api_method_response
        vllm.api_deploy


def test_public_internet_access():
    vllm = AwsVllmComponent(
        name="test",
        args=AwsVllmComponentArgs(
            public_internet_access=True,
        ),
    )

    assert isinstance(vllm.api, aws.apigateway.RestApi)
    assert isinstance(vllm.api_resource, aws.apigateway.Resource)
    assert isinstance(vllm.api_method, aws.apigateway.Method)
    assert isinstance(vllm.api_access_sagemaker_role, aws.iam.Role)
    assert isinstance(vllm.api_integration, aws.apigateway.Integration)
    assert isinstance(vllm.api_integration_response, aws.apigateway.IntegrationResponse)
    assert isinstance(vllm.api_method_response, aws.apigateway.MethodResponse)
    assert isinstance(vllm.api_deploy, aws.apigateway.Deployment)
