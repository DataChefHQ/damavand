from damavand.cloud.aws.controllers.llm import AwsLlmController


controller = AwsLlmController(
    name="my-dspy",
    region="eu-west-1",
)


def lambda_handler(event, context):
    question = event.get("question")
    role = event.get("role", "user")

    response = controller.client.chat.completions.create(
        model=controller.model_id,
        messages=[{"role": role, "content": question}],
    )

    return {
        "statusCode": 200,
        "headers": {"Content-Type": "application/json"},
        "body": response,
    }


if __name__ == "__main__":
    if not controller.is_runtime_execution:
        controller.provision()
