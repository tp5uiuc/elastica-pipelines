"""Test cases for core IO."""
import pytest

from elastica_pipelines.io.core import SystemRecord
from elastica_pipelines.io.protocols import ElasticaConvention


@pytest.fixture
def parent_v():
    """Get system record parent for testing."""

    def node_data(x, y):
        return {"k1": {"data": x}, "k2": {"data": y}}

    return {
        ElasticaConvention.as_system_key("100"): node_data(5, 10),
        ElasticaConvention.as_system_key("200"): node_data(20, 40),
    }


class TestSystemRecord:
    """Testing SystemRecord."""

    def test_getitem(self, parent_v) -> None:
        """Constructor test.

        Args:
            parent_v : The fixture to obtain parents.
        """
        s = SystemRecord(parent_v, sys_id=100)
        assert s["k1"] == 5
        assert s["k2"] == 10

        ys = SystemRecord(parent_v, sys_id=200)
        assert ys["k1"] == 20
        assert ys["k2"] == 40

    def test_transforms(self, parent_v) -> None:
        """Test transformation.

        Args:
            parent_v : The fixture to obtain parents.
        """

        def trafo(x):
            return x + 2

        s = SystemRecord(parent_v, sys_id=100, transforms=trafo)
        assert s["k1"] == trafo(5)
        assert s["k2"] == trafo(10)

    def test_len(self, parent_v) -> None:
        """Test length.

        Args:
            parent_v : The fixture to obtain parents.
        """
        s = SystemRecord(parent_v, sys_id=100)
        # There are only two keys.
        assert len(s) == 2
        # Add a keys check to ensure mapping works irrespective
        # of typing or collections.abc
        assert len(s.keys()) > 0

    def test_iter(self, parent_v) -> None:
        """Test iterator.

        Args:
            parent_v : The fixture to obtain parents.
        """
        s = SystemRecord(parent_v, sys_id=100)
        # There are only two keys.
        its = iter(s)
        assert next(its) == "k1"
        assert next(its) == "k2"
