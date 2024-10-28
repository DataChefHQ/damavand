from typing import NewType
from damavand.utils import is_building


if is_building():
    from pulumi import Resource as PulumiResource
else:
    PulumiResource = NewType("PulumiResource", None)
