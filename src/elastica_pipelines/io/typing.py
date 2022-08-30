"""Elastica IO typing."""
from typing import Any
from typing import Callable
from typing import Generic
from typing import Mapping
from typing import TypeVar
from typing import Union

import numpy.typing as npt
from typing_extensions import TypeAlias


# Functional
FuncType: TypeAlias = Callable[..., Any]
F = TypeVar("F", bound=FuncType)


Key: TypeAlias = Union[int, str, slice]
Node: TypeAlias = Mapping[str, Any]
Index: TypeAlias = Union[int, slice]
RecordConcept = TypeVar(
    "RecordConcept", bound=Mapping[str, npt.ArrayLike], covariant=True
)


class _R(Generic[RecordConcept]):
    pass


Record: TypeAlias = _R[Mapping[str, npt.ArrayLike]]
Records = TypeVar("Records", bound=Mapping[Key, Record], covariant=True)
RecordsSlice = TypeVar("RecordsSlice", bound=Mapping[Key, Record], covariant=True)


"""Old way of defining types, mypy deficiencies are rampant smh.
# Record: TypeAlias = Mapping[Key, npt.ArrayLike]
# Records = TypeVar("Records", bound=Mapping[Key, ConcreteRecord])
# RecordsSlice = TypeVar("RecordsSlice", bound=Mapping[Key, ConcreteRecord])
"""
