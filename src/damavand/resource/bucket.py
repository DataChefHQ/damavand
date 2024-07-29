from typing import Optional

from damavand.resource import BaseResource


class BaseObjectStorage(BaseResource):
    def __init__(
        self,
        name,
        id_: Optional[str] = None,
        tags: dict[str, str] = {},
        **kwargs,
    ) -> None:
        super().__init__(name, id_, tags, **kwargs)

    def provision(self):
        raise NotImplementedError

    def get_object(self, path: str) -> bytes:
        raise NotImplementedError

    def add_object(self, object: bytes, path: str):
        raise NotImplementedError

    def remove_object(self, path: str):
        raise NotImplementedError

    def list_objects(self) -> list[str]:
        raise NotImplementedError
