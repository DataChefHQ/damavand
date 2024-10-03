import logging
from typing import Any

from damavand.base.controllers import ApplicationController


logger = logging.getLogger(__name__)


class LlmController(ApplicationController):
    """ """

    def __init__(
        self,
        name,
        tags: dict[str, str] = {},
        **kwargs,
    ) -> None:
        ApplicationController.__init__(self, name, tags, **kwargs)
        self.applications: list[Any] = []
