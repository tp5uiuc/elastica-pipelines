"""Entry point into IO."""


import pathlib
import weakref
from typing import Optional
from typing import Union

from elastica_pipelines.io.backends import SupportedBackends
from elastica_pipelines.io.temporal import Series
from elastica_pipelines.io.typing import FuncType


def _check_ok(p: pathlib.Path) -> None:
    """Check if input path is okay to read from.

    Args:
        p(Path) : path of file to choose backend.

    Raises:
        FileNotFoundError: If p does not exist.
        OSError: If p is not a file.
    """
    if not p.exists():
        raise FileNotFoundError(f"File in path {p} not found.")

    if not p.is_file():
        raise OSError(f"Path {p} is not a valid file.")


def _choose_backend(p: pathlib.Path) -> SupportedBackends:
    """Choose backend based on file name.

    Args:
        p(Path) : path of file to choose backend.

    Returns:
        Supported Backend

    Raises:
        RuntimeError: If backend is unsupported.
    """
    _check_ok(p)

    def match(suffix: str) -> bool:
        return p.suffix == suffix

    if match(".h5"):
        return SupportedBackends.HDF5
    else:
        raise RuntimeError(f"Unsupported backend {p.suffix}")


def series(
    *,
    file_pattern: Optional[str] = None,
    metadata: Optional[Union[str, pathlib.Path]] = None,
    transforms: Optional[FuncType] = None,
) -> Series:
    """Make a Series from pattern or metadata file.

    Args:
        file_pattern (str, Optional): Naming pattern of time-series files.
        metadata : Metadata file.
        transforms (Callable, Optional): A function/transform that takes in an array
            data-structure and returns a transformed version.
            E.g, ``transforms.ToArray``

    Returns:
        Series object with temporal system evolution.

    Example:
        >>> from elastica_pipelines.io import series
        >>> metadata_fn = "tests/io/data/elastica_metadata.h5"
        >>> for t, snapshot in series(metadata=metadata_fn).iterations():
        >>>     print("Iteration: {0} at time {1}".format(t.iterate, t.time))

    Raises:
        RuntimeError: If none or both pattern and metadata is simultaneously specified.
        NotImplementedError: For pattern-based iteration.
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
