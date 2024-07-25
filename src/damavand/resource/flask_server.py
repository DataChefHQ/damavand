from typing import Optional, Any
from cdktf import TerraformStack
from flask import Flask

from damavand.resource import Resource, buildtime, runtime


class IFlaskServer(Resource, Flask):
    def __init__(
        self,
        import_name: str,
        name,
        stack: TerraformStack,
        id_: Optional[str] = None,
        tags: dict[str, str] = {},
        **kwargs,
    ) -> None:
        super().__init__(
            name,
            stack,
            id_,
            tags,
            import_name=import_name,
            **kwargs,
        )

    @buildtime
    def provision(self):
        raise NotImplementedError

    @runtime
    def run(
        self,
        host: str | None = None,
        port: int | None = None,
        debug: bool | None = None,
        load_dotenv: bool = True,
        **options: Any,
    ) -> None:
        return super().run(host, port, debug, load_dotenv, **options)
