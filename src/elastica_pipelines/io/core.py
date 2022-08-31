"""Core IO types."""
from typing import Any
from typing import Iterator
from typing import Optional
from typing import Type
from typing import Union

import numpy.typing as npt

from elastica_pipelines.io.protocols import ElasticaConvention
from elastica_pipelines.io.protocols import HasRecordTraits
from elastica_pipelines.io.protocols import RecordTraits
from elastica_pipelines.io.protocols import _ErrorOutTraits
from elastica_pipelines.io.protocols import record_type
from elastica_pipelines.io.protocols import slice_type
from elastica_pipelines.io.transforms import Compose
from elastica_pipelines.io.typing import FuncType
from elastica_pipelines.io.typing import Key
from elastica_pipelines.io.typing import Node
from elastica_pipelines.io.typing import Record
from elastica_pipelines.io.typing import Records
from elastica_pipelines.io.typing import RecordsSlice


class SystemRecord(Record):
    """Base record for an Elastica++ data-structure.

    Is intended to be specialized for different Elastica++ data-stuctures via a traits
    class.

    Args:
        node (node): Node node in which to lookup the current system record.
        sys_id (int): Unique system id of the record to lookup.
        transforms (callable, optional): A function/transform that takes in an array
            data-structure and returns a transformed version.
            E.g, ``transforms.ToArray``

    .. note::
            This is decoupled from records because this is a node that deals with purely
            string based lookup.
    """

    def __init__(self, node: Node, sys_id: int, transforms: Optional[FuncType] = None):
        """Init."""
        self.node = node
        self.sys_id = sys_id
        # Add a lambda to WAR weird mypy bugs
        # access may not be needed for general node types
        self.transforms: FuncType = Compose(
            (ElasticaConvention.access, transforms or (lambda x: x))
        )

    def lazy_lookup(self) -> Any:
        """Lazily lookup an Elastica++ data-structure from records."""
        return self.node[ElasticaConvention.as_system_key(self.sys_id)]

    def __getitem__(self, k: str) -> npt.ArrayLike:  # noqa
        return self.transforms(self.lazy_lookup()[k])

    def __iter__(self) -> Iterator[str]:  # noqa
        return iter(self.lazy_lookup())

    def __len__(self) -> int:  # noqa
        return len(self.lazy_lookup())


def _validate(length: int, index: int) -> int:
    """Validate an index based on length.

    Args:
        length (int): Length of data-structure.
        index (int): Indices to be validated.

    Returns:
        Validated index satisfying 0 <= ``index`` < ``length``

    Raises:
        KeyError: If index is out of bounds.
    """
    if index < 0:
        index += length
    if index < 0 or index >= length:
        raise KeyError(f"{index}")
    return index


# Can defined a new protocol for mapping
# @overload
# def __getitem__(self, k: int) -> Record:
#     ...

# @overload
# def __getitem__(self, k: str) -> Record:
#     ...

# @overload
# def __getitem__(self, k: slice) -> RecordsSlice:
#     ...


class SystemRecords(Records, HasRecordTraits):
    """Base record collection for Elastica++ data-structures.

    Is intended to be specialized for different Elastica++ data-stuctures via a traits
    class.

    Args:
        node (node): Node node in which to lookup the current system record.
        transforms (callable, optional): A function/transform that takes in an array
            data-structure and returns a transformed version.
            E.g, ``transforms.ToArray``
    """

    """These traits are not used, but are required to keep the static type-checkers
    quiet."""
    traits: RecordTraits = _ErrorOutTraits()

    def __init__(self, node: Node, transforms: Optional[FuncType] = None) -> None:
        """Initializer."""
        self.node = node
        self.transforms = transforms

    def __iter__(self) -> Iterator[int]:  # noqa
        for x in self.node:
            yield int(x)

    def __len__(self) -> int:  # noqa
        return len(self.node)

    def __getitem__(self, k: Key) -> Union[Record, RecordsSlice]:  # noqa
        length = len(self)
        if isinstance(k, int):
            rt: Type[Record] = record_type(self)
            return rt(self.node, _validate(length, k), self.transforms)
        elif isinstance(k, slice):
            st: Type[RecordsSlice] = slice_type(self)
            return st(self, slice(*k.indices(length)))
        elif isinstance(k, str):
            return self.__getitem__(int(k))
        else:
            raise TypeError(f"Invalid argument type: {type(k)}")
