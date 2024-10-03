import json
import dspy


def default_question(connection: dspy.OpenAI, question: str) -> dict:
    dspy.settings.configure(lm=connection)
    predict = dspy.Predict("question -> answer")
    answer = predict(question=question)

    return {
        "statusCode": 200,
        "headers": {"Content-Type": "application/json"},
        "body": json.dumps({"response": answer}),
    }
