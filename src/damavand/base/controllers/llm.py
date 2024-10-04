import logging

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
