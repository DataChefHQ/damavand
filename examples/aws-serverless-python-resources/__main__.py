import pulumi_aws as aws

from damavand.cloud.aws.resources.serverless_python_component import (
    AwsServerlessPythonComponent,
    AwsServerlessPythonComponentArgs,
)


def main() -> None:
    AwsServerlessPythonComponent(
        name="python-serverless-example",
        args=AwsServerlessPythonComponentArgs(
            python_version=aws.lambda_.Runtime.PYTHON3D11,
        ),
    )


if __name__ == "__main__":
    main()
