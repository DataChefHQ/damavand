from typing import Optional
from cdktf import TerraformStack

from damavand.resource import Resource


class IBucket(Resource):
    def __init__(
        self,
        name,
        stack: TerraformStack,
        id_: Optional[str] = None,
        tags: dict[str, str] = {},
        **kwargs,
    ) -> None:
        super().__init__(name, stack, id_, tags, **kwargs)

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
