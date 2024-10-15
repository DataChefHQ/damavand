import logging
from typing import Any

from damavand.base.controllers import ApplicationController
from damavand.base.controllers.base_controller import runtime

from sparkle.application import Sparkle


logger = logging.getLogger(__name__)


class SparkController(ApplicationController):
    """
    The SparkController class is the base class for all Spark controllers
    implementations for each cloud provider.

    ...

    Attributes
    ----------
    name : str
        the name of the controller.
    applications : list[Sparkle]
        the list of Spark applications.
    tags : dict[str, str]
        the tags of the controller.
    resource_args : Any
        Any extra arguments for the underlying resource.
    kwargs : dict
        the extra arguments.

    Methods
    -------
    application_with_id(app_id)
        Return the Spark application with the given ID.
    run_application(app_id)
        Run the Spark application with the given ID.
    """

    def __init__(
        self,
        name,
        applications: list[Sparkle],
        tags: dict[str, str] = {},
        resource_args: Any = None,
        **kwargs,
    ) -> None:
        ApplicationController.__init__(self, name, tags, **kwargs)
        self.applications: list[Sparkle] = applications

    def application_with_id(self, app_id: str) -> Sparkle:
        """Return the Spark application with the given ID.

        Args:
            app_id (str): The application ID.

        Returns:
            Sparkle: The Spark application.
        """
        for app in self.applications:
            if app.config.app_id == app_id:
                return app

        raise ValueError(f"Application with ID {app_id} not found.")

    @runtime
    def run_application(self, app_id: str) -> None:
        """Run the Spark application with the given ID.

        Args:
            app_id (str): The application ID.
        """

        app = self.application_with_id(app_id)
        df = app.process()
        app.write(df)
