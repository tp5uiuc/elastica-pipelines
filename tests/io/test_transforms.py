"""Test cases for IO transformations."""
import numpy as np

from elastica_pipelines.io.transforms import Compose
from elastica_pipelines.io.transforms import ToArray


def test_compose() -> None:
    """Test composition of functions."""
    fun = Compose((lambda x: x + 2, lambda x: x * 2))
    assert fun(2) == 8
    substrings = (
        "Compose",
        "lambda",
    )
    assert all(map(lambda x: x in fun.__repr__(), substrings))


def test_to_array() -> None:
    """Test ToArray."""
    a = [1, 2, 3, 4]
    fun = ToArray()
    b = fun(a)
    assert type(b) == np.ndarray
    assert b.shape == (4,)
    assert "ToArray" in fun.__repr__()
