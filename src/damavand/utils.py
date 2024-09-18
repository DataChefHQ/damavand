import os
import re


def is_building():
    """Check if the application is being built or run"""

    return os.environ.get("MODE", "RUN") == "BUILD"


def error_code_from_boto3(e):
    """Extract error code from boto3 exception"""

    return e.response.get("Error", {}).get("Code")


def to_camel_case(input_string: str) -> str:
    """Convert a string to camel case"""

    input_string = input_string.strip()
    cleaned_string = re.sub(r"[^a-zA-Z0-9]+", " ", input_string)
    words = cleaned_string.split()
    camel_case_string = "".join(word.capitalize() for word in words)

    return camel_case_string
