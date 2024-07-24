import os


def is_building():
    """Check if the application is being built or run"""

    return os.environ.get("MODE", "RUN") == "BUILD"
