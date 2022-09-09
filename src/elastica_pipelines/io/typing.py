"""Elastica IO typing."""
from __future__ import annotations

from typing import Any
from typing import Callable
from typing import List
from typing import Mapping
from typing import Optional
from typing import TypeVar
from typing import Union

import numpy.typing as npt
from typing_extensions import TypeAlias


# Functional
FuncType: TypeAlias = Callable[..., Any]
F = TypeVar("F", bound=FuncType)


Key: TypeAlias = Union[int, str, List[int], slice]
Node: TypeAlias = Mapping[str, Any]
Indices: TypeAlias = Union[int, slice, List[int]]


class _RecordImplementation(Mapping[str, npt.ArrayLike]):
    def __init__(
        self, parent: Node, sys_id: int, transforms: Optional[FuncType]  # noqa
    ) -> None:
        ...  # pragma: no cover


Record: TypeAlias = _RecordImplementation
RecordLeafs = Union[Record, "RecordsSlice"]


class _RecordsImplementation(Mapping[Key, RecordLeafs]):
    def __init__(self, parent: Node, transforms: Optional[FuncType]) -> None:  # noqa
        ...  # pragma: no cover


Records: TypeAlias = _RecordsImplementation


class _RecordSliceImplementation(Mapping[Key, RecordLeafs]):
    def __init__(self, parent: Records, indices: Indices) -> None:  # noqa
        ...  # pragma: no cover


RecordsSlice: TypeAlias = _RecordSliceImplementation

"""Old way of defining types, mypy deficiencies are rampant smh.
# Record: TypeAlias = Mapping[Key, npt.ArrayLike]
# Records = TypeVar("Records", bound=Mapping[Key, ConcreteRecord])
# RecordsSlice = TypeVar("RecordsSlice", bound=Mapping[Key, ConcreteRecord])
"""
