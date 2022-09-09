"""Transformations to apply when reading/writing Elastica IO."""
from typing import Any
from typing import Sequence
from typing import Tuple

import numpy as np
import numpy.typing as npt

from elastica_pipelines.io.typing import FuncType


class Compose:
    """Composes several transforms together.

    Args:
        transforms (list of ``Transform`` objects): list of transforms to compose.

    Example:
        >>> from elastica_pipelines.io.transforms import Compose, ToArray
        >>> Compose([
        >>>     ToArray(),
        >>> ])
    """

    def __init__(self, transforms: Sequence[FuncType]):
        """Initializes transforms."""
        self.transforms: Tuple[FuncType, ...] = tuple(transforms)

    def __call__(self, obj: Any) -> Any:
        """Applies transformation to object.

        Args:
            obj : Any object

        Returns:
            Transformed object.
        """
        # Prefer this over functools compose for user-friendliness
        for t in self.transforms:
            obj = t(obj)
        return obj

    def __repr__(self) -> str:  # noqa
        format_string = self.__class__.__name__ + "("
        for t in self.transforms:
            format_string += "\n"
            format_string += f"    {t}"
        format_string += "\n)"
        return format_string


class ToArray:
    """Convert a ``HDF5 dataset`` or ``numpy.ndarray`` to ``numpy.ndarray``.

    Example:
        >>> from elastica_pipelines.io.transforms import ToArray
        >>> ToArray()([1, 2, 3, 4]).shape
    """

    def __init__(self) -> None:  # noqa
        pass

    def __call__(self, tensor: npt.ArrayLike) -> npt.NDArray[Any]:
        """Applies array transformation.

        Args:
            tensor (HDF5 dataset or numpy.ndarray): Tensor to be converted to ndarray.

        Returns:
            Tensor: Converted data.
        """
        return np.asarray(tensor)

    def __repr__(self) -> str:  # noqa
        return f"{self.__class__.__name__}()"
