from typing import Iterable

from damavand.base.controllers import ApplicationController


class ObjectStorageController(ApplicationController):
    def __init__(
        self,
        name,
        tags: dict[str, str] = {},
        **kwargs,
    ) -> None:
        super().__init__(name, tags, **kwargs)

    def read(self, path: str) -> bytes:
        """Read an object from the storage."""
        raise NotImplementedError

    def write(self, object: bytes, path: str):
        """Write an object"""
        raise NotImplementedError

    def delete(self, path: str):
        """Delete an object from the storage."""
        raise NotImplementedError

    def list(self) -> Iterable[str]:
        """
        Return an iterable of object keys in the bucket.

        __ATTENTION__: This method is expensive for large storages as it request multiple times to fetch all objects.
        """
        raise NotImplementedError

    def exist(self, path: str) -> bool:
        """Check if an object exists in the storage."""
        raise NotImplementedError
