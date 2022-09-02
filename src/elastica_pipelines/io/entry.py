"""Entry point into IO."""


import pathlib
import weakref
from os import PathLike
from typing import Optional
from typing import Union

from elastica_pipelines.io.backends import SupportedBackends
from elastica_pipelines.io.temporal import Series
from elastica_pipelines.io.typing import FuncType


def _choose_backend(p: pathlib.Path) -> SupportedBackends:
    """Choose backend based on file name.

    Args:
        p(Path) : path of file to choose backend

    Returns:
        Supported Backend

    Raises:
        RuntimeError: If backend is unsupported
    """
    if not p.exists():
        raise FileNotFoundError(f"File in path {p} not found.")

    def match(suffix: str) -> bool:
        return p.is_file() and p.suffix == suffix

    if match(".h5"):
        return SupportedBackends.HDF5
    else:
        raise RuntimeError(f"Unsupported backend {p.suffix}")


def series(
    *,
    file_pattern: Optional[str] = None,
    metadata: Optional[Union[str, PathLike[str]]] = None,
    transforms: Optional[FuncType] = None,
) -> Series:
    """Make a Series from pattern or metadata file.

    Args:
        file_pattern (str, optional): Naming pattern of time-series files.
        metadata (str, optional): Metadata file.
        transforms (callable, optional): A function/transform that takes in an array
            data-structure and returns a transformed version.
            E.g, ``transforms.ToArray``
    """
    if not (file_pattern or metadata):
        raise RuntimeError(
            "Either a pattern string or metadata file needs to be specified."
        )

    if file_pattern and metadata:
        raise RuntimeError(
            "Both pattern string or metadata file cannot be specified "
            "simultaneously, choose one."
        )

    if file_pattern:
        raise NotImplementedError("Pattern based series matching is not implemented.")

    if metadata:
        # else metadata file
        md = pathlib.Path(metadata)
        backend = _choose_backend(md)
        if backend == SupportedBackends.HDF5:
            import h5py  # type: ignore[import]

            f = h5py.File(md, "r")
            s = Series(f, transforms=transforms)
            weakref.finalize(s, lambda x: x.close(), f)
            return s

    return Series({}, transforms=transforms)  # pragma: no cover
