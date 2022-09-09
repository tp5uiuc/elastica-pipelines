"""Tests for different backends."""
import pathlib

import h5py
import pytest

from elastica_pipelines.io.backends import HDF5Access
from elastica_pipelines.io.backends import accessor
from tests.io.test_protocols import skip_if_env_has


@pytest.fixture()
def node_data_path(tmp_path) -> pathlib.Path:
    """Prepares node_data and returns path.

    Args:
        tmp_path: Temporary path fixture.

    Returns:
        Path file.
    """
    f = tmp_path / "node_data.h5"
    hf = h5py.File(f, "w")
    time_metadata_group = hf.create_group("TimeMetadata")
    # time_group = time_metadata_group.create_group("time")
    time_metadata_group.create_dataset("time", data=0.2)
    # dt_group = time_metadata_group.create_group("dt")
    time_metadata_group.create_dataset("dt", data=0.02)
    hf.create_dataset("data", data=2)
    hf.close()
    return f


@pytest.fixture()
def node_data(node_data_path) -> h5py.File:
    """Opens node_data for reading.

    Args:
        node_data_path: Path fixture.

    Returns:
        HDF5 file for reading.
    """
    return h5py.File(node_data_path, "r")


class TestHDF5Access:
    """Test suite for HDF5 Access."""

    def test_access_time(self, node_data) -> None:
        """Tests time access.

        Args:
            node_data : Fixture for testing.
        """
        assert HDF5Access.access_time(node_data) == 0.2

    def test_access_dt(self, node_data) -> None:
        """Tests dt access."""
        ...
        assert HDF5Access.access_dt(node_data) == 0.02

    def test_access_data(self, node_data) -> None:
        """Tests data access."""
        assert HDF5Access.access_data(node_data)[()] == 2


@skip_if_env_has("typeguard")
def test_accessor() -> None:
    """Test accessor."""
    # FIXME : different backends in the future.
    t = accessor({"1": 2})
    assert t == HDF5Access
