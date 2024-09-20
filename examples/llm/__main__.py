from damavand.cloud.aws.resources import AwsVllmComponent, AwsVllmComponentArgs


def main() -> None:
    AwsVllmComponent(
        name="my-vllm",
        args=AwsVllmComponentArgs(
            region="eu-west-1",
            public_internet_access=True,
        ),
    )


if __name__ == "__main__":
    main()
