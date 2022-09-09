"""Core IO types."""
from __future__ import annotations

from typing import Any
from typing import ClassVar
from typing import Iterator
from typing import List
from typing import Optional
from typing import Type
from typing import Union
from typing import overload

import numpy.typing as npt

from elastica_pipelines.io.protocols import ElasticaConvention
from elastica_pipelines.io.protocols import RecordTraits
from elastica_pipelines.io.protocols import _ErrorOutTraits
from elastica_pipelines.io.protocols import record_type
from elastica_pipelines.io.protocols import slice_type
from elastica_pipelines.io.transforms import Compose
from elastica_pipelines.io.typing import FuncType
from elastica_pipelines.io.typing import Indices
from elastica_pipelines.io.typing import Key
from elastica_pipelines.io.typing import Node
from elastica_pipelines.io.typing import Record
from elastica_pipelines.io.typing import RecordLeafs
from elastica_pipelines.io.typing import Records
from elastica_pipelines.io.typing import RecordsSlice


class SystemRecord(Record):
    """Base record for an Elastica++ data-structure.

    Is intended to be specialized for different Elastica++ data-stuctures via a traits
    class.

    Args:
        node (node): Node node in which to lookup the current system record.
        sys_id (int): Unique system id of the record to lookup.
        transforms (Callable, Optional): A function/transform that takes in an array
            data-structure and returns a transformed version.
            E.g, ``transforms.ToArray``

    .. note::
            This is decoupled from records because this is a node that deals with purely
            string based lookup.
    """

    def __init__(
        self, node: Node, sys_id: int, transforms: Optional[FuncType] = None
    ) -> None:
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


"""Implementation of system-records specific functionality."""


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


class SystemRecords(Records):
    """Base record collection for Elastica++ data-structures.

    Is intended to be specialized for different Elastica++ data-stuctures via a traits
    class.

    Args:
        node (node): Node node in which to lookup the current system record.
        transforms (Callable, Optional): A function/transform that takes in an array
            data-structure and returns a transformed version.
            E.g, ``transforms.ToArray``
    """

    """These traits are not used, but are required to keep the static type-checkers
    quiet."""
    traits: ClassVar[Type[RecordTraits]] = _ErrorOutTraits

    def __init__(self, node: Node, transforms: Optional[FuncType] = None) -> None:
        """Initializer."""
        self.node = node
        self.transforms = transforms

    def __iter__(self) -> Iterator[int]:  # noqa
        for x in self.node:
            yield int(x)

    def __len__(self) -> int:  # noqa
        return len(self.node)

    def __getitem__(self, k: Key) -> RecordLeafs:  # noqa
        length = len(self)
        if isinstance(k, int):
            rt: Type[Record] = record_type(self)
            return rt(self.node, _validate(length, k), self.transforms)
        elif isinstance(k, slice):
            st: Type[RecordsSlice] = slice_type(self)
            return st(self, slice(*k.indices(length)))
        elif isinstance(k, list):
            it: Type[RecordsSlice] = slice_type(self)
            return it(self, k)
        elif isinstance(k, str):
            return self.__getitem__(int(k))
        else:
            raise TypeError(f"Invalid argument type: {type(k)}")


"""Implementation of system-slice specific functionality."""


class RecordsIndexedOp:
    """Operations on a discrete indices of a record.

    Args:
        indices (int, List[int]) : indices on which the record is sliced.
    """

    def __init__(self, indices: Union[int, List[int]]) -> None:  # noqa
        self.value = [indices] if isinstance(indices, int) else indices

    def get_length_of_slice(self, length: int) -> int:
        """Get length of slice.

        Args:
            length: Length from which we obtain the slice length.

        Returns:
            Length of the slice.
        """
        return len(self.value)

    @overload
    def get_index_into_slice(self, k: int, length: int) -> int:  # noqa
        ...  # pragma: no cover

    @overload
    def get_index_into_slice(self, k: slice, length: int) -> List[int]:  # noqa
        ...  # pragma: no cover

    @overload
    def get_index_into_slice(self, k: List[int], length: int) -> List[int]:  # noqa
        ...  # pragma: no cover

    def get_index_into_slice(self, k: Indices, length: int) -> Union[List[int], int]:
        """Gets index into slice.

        Args:
            k (Indices): Set of indices into the record slice.
            length (int): Length of the record slice.

        Returns:
            Indices into the record slice.
        """
        if isinstance(k, (int, slice)):
            return self.value[k]
        else:
            return [self.value[j] for j in k]


class RecordsSliceOp:
    """Operations on a slice of a record.

    Args:
        indices (slice) : slice onto which the record is sliced.
    """

    def __init__(self, indices: slice) -> None:  # noqa
        self.value = indices

    def get_length_of_slice(self, length: int) -> int:
        """Get length of slice.

        Args:
            length: Length from which we obtain the slice length.

        Returns:
            Length of the slice.
        """
        return len(range(*self.value.indices(length)))

    @overload
    def get_index_into_slice(self, k: int, length: int) -> int:  # noqa
        ...  # pragma: no cover

    @overload
    def get_index_into_slice(self, k: slice, length: int) -> slice:  # noqa
        ...  # pragma: no cover

    @overload
    def get_index_into_slice(self, k: List[int], length: int) -> List[int]:  # noqa
        ...  # pragma: no cover

    def get_index_into_slice(self, k: Indices, length: int) -> Indices:
        """Gets index into slice.

        Args:
            k (Indices): Set of indices into the record slice.
            length (int): Length of the record slice.

        Returns:
            Indices into the record slice.
        """
        if isinstance(k, int):
            return self.value.start + self.value.step * _validate(length, k)
        elif isinstance(k, slice):
            c_start, c_stop, c_step = k.indices(length)
            p_start, _, p_step = self.value.start, self.value.stop, self.value.step
            start = p_start + p_step * c_start
            stop = p_start + p_step * c_stop
            step = p_step * c_step
            return slice(start, stop, step)
        else:
            return [self.get_index_into_slice(j, length) for j in k]


class SystemRecordsSlice(RecordsSlice):
    """Base class for a slice of io.SystemRecords.

    Is intended to be specialized for different Elastica++ data-stuctures via a traits
    class.

    Args:
        parent (Records): Parent records object lookup the system records.
        index (Indices): Datastructure satisfying ``Indices`` requirements.
    """

    def __init__(self, parent: SystemRecords, indices: Indices) -> None:
        """Initializer."""
        self.parent = parent
        self.indices: Union[RecordsIndexedOp, RecordsSliceOp] = (
            RecordsSliceOp(indices)
            if isinstance(indices, slice)
            else RecordsIndexedOp([indices])
            if isinstance(indices, int)
            else RecordsIndexedOp(indices)
        )

    def __iter__(self) -> Iterator[int]:  # noqa
        # Implemented as integers from 0 to len() instead of parent to
        # have consistent API usage.
        yield from range(len(self))

    def __len__(self) -> int:  # noqa
        return self.indices.get_length_of_slice(len(self.parent))

    def __getitem__(self, k: Key) -> RecordLeafs:  # noqa
        if isinstance(k, str):
            return self.__getitem__(int(k))
        elif isinstance(k, (int, list, slice)):
            return self.parent.__getitem__(
                self.indices.get_index_into_slice(k, len(self))
            )
        else:
            # Parent raises the appropriate error if type is incorrect.
            return self.parent.__getitem__(k)  # type: ignore[unreachable]
