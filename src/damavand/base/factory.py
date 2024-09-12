from dataclasses import field, dataclass
from typing import Optional, Generic, TypeVar

from damavand.base.controllers import ApplicationController
from damavand.cloud.provider import AwsProvider, AzurermProvider, CloudProvider

from damavand.errors import UnsupportedProvider


ControllerType = TypeVar("ControllerType", bound=ApplicationController)


@dataclass
class ApplicationControllerFactory(Generic[ControllerType]):
    """
    A base generic controller factory class to provide common interface to create application controllers for different cloud provider.

    ...
    Attributes
    ----------
    provider : CloudProvider
        The cloud provider object.
    tags : dict[str, str]
        A set of default tags to be applied to all resources.
    provision_on_creation : bool
        A flag to provision resources on creation of the controller. If set to False, the resources must be provisioned manually.

    Methods
    -------
    new(name: str, id: Optional[str] = None, **kwargs) -> ControllerType
        Create a new application controller.
    """

    provider: CloudProvider
    tags: dict[str, str] = field(default_factory=dict)
    provision_on_creation: bool = True
    controllers: list[ApplicationController] = field(init=False, default_factory=list)

    def new(
        self,
        name: str,
        id: Optional[str] = None,
        **kwargs,
    ) -> ControllerType:
        match self.provider:
            case AwsProvider():
                ctr = self._new_aws_controller(
                    name=name,
                    region=self.provider.enforced_region,
                    id=id,
                    tags=self.tags,
                    **kwargs,
                )

                if self.provision_on_creation:
                    ctr.provision()

                return ctr
            case AzurermProvider():
                ctr = self._new_azure_controller(
                    name=name,
                    id=id,
                    tags=self.tags,
                    **kwargs,
                )

                if self.provision_on_creation:
                    ctr.provision()

                return ctr
            case _:
                raise UnsupportedProvider(module=self.__class__.__name__)

    def _new_aws_controller(
        self,
        name: str,
        region: str,
        id: Optional[str] = None,
        tags: dict[str, str] = {},
        **kwargs,
    ) -> ControllerType:
        raise NotImplementedError()

    def _new_azure_controller(
        self,
        name: str,
        id: Optional[str] = None,
        tags: dict[str, str] = {},
        **kwargs,
    ) -> ControllerType:
        raise NotImplementedError()
