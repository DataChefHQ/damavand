import requests
import os

from damavand.cloud.aws.controllers.llm import AwsLlmController


controller = AwsLlmController(
    name="my-dspy",
    region="eu-west-1",
)


def ask(question: str, role: str) -> None:
    headers = {
        "Content-Type": "application/json",
    }

    json_data = {
        "messages": [
            {
                "role": role,
                "content": question,
            },
        ],
        "parameters": {
            "max_new_tokens": 400,
        },
        "stream": False,
    }

    return requests.post(
        controller.chat_completions_url,
        headers=headers,
        json=json_data,
    ).json()


def lambda_handler(event, context):
    question = event.get("question")
    role = event.get("role", "user")
    return ask(question, role)


if __name__ == "__main__":
    if not controller.is_runtime_execution:
        controller.provision()
    else:
        event = {
            "question": os.environ.get("QUESTION", "What is the capital of France?"),
            "role": os.environ.get("ROLE", "user"),
        }
        context = {}
        print(lambda_handler(event, context))
