from typing import Iterable, Optional

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

    def read(self, path: str) -> bytes:
        raise NotImplementedError

    def write(self, object: bytes, path: str):
        raise NotImplementedError

    def delete(self, path: str):
        raise NotImplementedError

    def list(self) -> Iterable[str]:
        """
        Return an iterable of object keys in the bucket.

        __ATTENTION__: This method is expensive for large buckets as it request multiple times to fetch all objects.
        """
        raise NotImplementedError
