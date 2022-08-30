"""Core IO types."""
from collections.abc import Iterator
from typing import Any
from typing import Mapping
from typing import Optional

import numpy.typing as npt

from elastica_pipelines.io.protocols import ElasticaConvention
from elastica_pipelines.io.transforms import Compose
from elastica_pipelines.io.typing import FuncType
from elastica_pipelines.io.typing import Node


class SystemRecord(Mapping[str, npt.ArrayLike]):
    """Base record for an Elastica++ data-structure.

    Is intended to be specialized for different Elastica++ data-stuctures via a traits
    class.

    Args:
        parent (node): Parent node in which to lookup the current system record.
        sys_id (int): Unique system id of the record to lookup.
        transforms (callable, optional): A function/transform that takes in an array
            data-structure and returns a transformed version.
            E.g, ``transforms.ToArray``

    .. note::
            This is decoupled from records because this is a node that deals with purely
            string based lookup.
    """

    def __init__(
        self, parent: Node, sys_id: int, transforms: Optional[FuncType] = None
    ):
        """Init."""
        self.parent = parent
        self.sys_id = sys_id
        # Add a lambda to WAR weird mypy bugs
        # access may not be needed for general node types
        self.transforms: FuncType = Compose(
            (ElasticaConvention.access, transforms or (lambda x: x))
        )

    def lazy_lookup(self) -> Any:
        """Lazily lookup an Elastica++ data-structure from records."""
        return self.parent[ElasticaConvention.as_system_key(self.sys_id)]

    def __getitem__(self, k: str) -> npt.ArrayLike:  # noqa
        return self.transforms(self.lazy_lookup()[k])

    def __iter__(self) -> Iterator[str]:  # noqa
        return iter(self.lazy_lookup())

    def __len__(self) -> int:  # noqa
        return len(self.lazy_lookup())
