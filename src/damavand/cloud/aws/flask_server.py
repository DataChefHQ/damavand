import os
import json
import logging
from constructs import Construct
from cdktf import TerraformAsset, AssetType
from cdktf_cdktf_provider_aws.iam_role import IamRole
from cdktf_cdktf_provider_aws.iam_role_policy_attachment import IamRolePolicyAttachment
from cdktf_cdktf_provider_aws.lambda_function import (
    LambdaFunction,
    LambdaFunctionEnvironment,
)
from cdktf_cdktf_provider_aws.lambda_permission import LambdaPermission
from cdktf_cdktf_provider_aws.apigatewayv2_api import (
    Apigatewayv2Api,
    Apigatewayv2ApiCorsConfiguration,
)
from typing import Optional
from cdktf import TerraformStack

from damavand.resource import IFlaskServer, buildtime


logger = logging.getLogger(__name__)


class AwsFlaskServer(IFlaskServer):
    def __init__(
        self,
        import_name: str,
        name,
        stack: TerraformStack,
        id_: Optional[str] = None,
        tags: dict[str, str] = {},
        **kwargs,
    ) -> None:
        super().__init__(import_name, name, stack, id_, tags, **kwargs)

    @buildtime
    def provision(self):
        if self.id_ is None:
            self.id_ = self.name
            logger.info(f"id_ is not provided. Using name as id_ {self.id_}")

        self.__cdktf_object = ApiConstruct(
            self.stack,
            self.id_,
            self.name,
            source_dir=os.getcwd(),
        )


class ApiConstruct(Construct):
    def __init__(
        self,
        scope: Construct,
        id: str,
        name: str,
        source_dir: str,
        environment_variables: dict[str, str] = {},
    ):
        super().__init__(scope, id)

        self.execution_role = IamRole(
            self,
            "lambda-exec",
            name=f"{name.lower()}-lambda-exec-role",
            assume_role_policy=json.dumps(
                {
                    "Version": "2012-10-17",
                    "Statement": {
                        "Action": "sts:AssumeRole",
                        "Principal": {
                            "Service": "lambda.amazonaws.com",
                        },
                        "Effect": "Allow",
                        "Sid": "",
                    },
                }
            ),
            inline_policy=[],
        )

        IamRolePolicyAttachment(
            self,
            "lambda-managed-policy",
            policy_arn="arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole",
            role=self.execution_role.name,
        )

        asset = TerraformAsset(
            self,
            "lambda-asset",
            path=source_dir,
            type=AssetType.ARCHIVE,
        )

        self.lambda_function = LambdaFunction(
            self,
            "api",
            function_name=f"{name.lower()}-lambda-function",
            handler="index.lambda_handler",
            runtime="python3.9",
            role=self.execution_role.arn,
            filename=asset.path,
            source_code_hash=asset.asset_hash,
            environment=LambdaFunctionEnvironment(
                variables=environment_variables,
            ),
        )

        self.api_gateway = Apigatewayv2Api(
            self,
            "api-gw",
            name=f"{name.lower()}-api-gw",
            protocol_type="HTTP",
            target=self.lambda_function.arn,
            cors_configuration=Apigatewayv2ApiCorsConfiguration(
                allow_origins=["*"], allow_methods=["*"], allow_headers=["*"]
            ),
        )

        LambdaPermission(
            self,
            "apigw-lambda",
            function_name=self.lambda_function.function_name,
            action="lambda:InvokeFunction",
            principal="apigateway.amazonaws.com",
            source_arn="{}/*/*".format(self.api_gateway.execution_arn),
        )
