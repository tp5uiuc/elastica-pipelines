"""Elastica IO typing."""
from typing import Any
from typing import Generic
from typing import Mapping
from typing import TypeVar
from typing import Union

import numpy.typing as npt
from typing_extensions import TypeAlias


Key: TypeAlias = Union[int, str]
Node: TypeAlias = Mapping[str, Any]
Index: TypeAlias = Union[int, slice]
Record = TypeVar("Record", bound=Mapping[Key, npt.ArrayLike], covariant=True)


class _R(Generic[Record]):
    pass


ConcreteRecord = TypeVar("ConcreteRecord", bound=_R[Mapping[Key, npt.ArrayLike]])
Records: TypeAlias = Mapping[Key, ConcreteRecord]
RecordsSlice: TypeAlias = Mapping[Key, ConcreteRecord]


"""Old way of defining types, mypy deficiencies are rampant smh.
# Record: TypeAlias = Mapping[Key, npt.ArrayLike]
# Records = TypeVar("Records", bound=Mapping[Key, ConcreteRecord])
# RecordsSlice = TypeVar("RecordsSlice", bound=Mapping[Key, ConcreteRecord])
"""
