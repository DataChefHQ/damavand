import os
from controller import AwsDspyController
from damavand.environment import Environment

controller = AwsDspyController(
    name="my-dspy",
    region="eu-west-1",
)


def lambda_handler(event, context):
    return controller.build_or_run(
        app_id=event.get("app_id", "default"),
        question=event.get("question", "What llm are you?"),
    )


if __name__ == "__main__":
    if controller.environment == Environment.LOCAL:
        # run the lambda handler locally
        event = {
            "app_id": os.environ.get("APP_ID", "default"),
            "question": os.environ.get("QUESTION", "What llm are you?"),
        }
        context = {}

        if response := lambda_handler(event, context):
            print(response)
    else:
        # aws automatically calls lambda_handler
        pass
