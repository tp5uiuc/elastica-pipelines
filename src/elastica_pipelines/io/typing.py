"""Elastica IO typing."""
from typing import Any
from typing import Mapping
from typing import Union

import numpy.typing as npt
from typing_extensions import TypeAlias


Key: TypeAlias = Union[int, str]
Node: TypeAlias = Mapping[str, Any]
Index: TypeAlias = Union[int, slice]
Record: TypeAlias = Mapping[Key, npt.ArrayLike]
Records: TypeAlias = Mapping[Key, Record]
RecordsSlice: TypeAlias = Mapping[Key, Record]
