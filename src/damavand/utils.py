import os


def is_building():
    """Check if the application is being built or run"""

    return os.environ.get("MODE", "RUN") == "BUILD"


def error_code_from_boto3(e):
    """Extract error code from boto3 exception"""

    return e.response.get("Error", {}).get("Code")
