"""Test cases for temporal IO types."""
import pytest

from elastica_pipelines.io.core import SystemRecord
from elastica_pipelines.io.protocols import ElasticaConvention
from elastica_pipelines.io.specialize import CosseratRodRecords
from elastica_pipelines.io.specialize import CosseratRodRecordTraits
from elastica_pipelines.io.specialize import SphereRecords
from elastica_pipelines.io.specialize import SphereRecordTraits
from elastica_pipelines.io.temporal import RecordsAdapter
from elastica_pipelines.io.temporal import RecordsAdapterKey
from elastica_pipelines.io.temporal import Snapshot
from elastica_pipelines.io.typing import Node
from tests.io.test_core import node_v  # noqa : F401
from tests.io.test_core import records_v  # noqa : F401
from tests.io.test_protocols import skip_if_env_has


class TestRecordsAdapter:
    """Testing RecordsAdapter."""

    def test_len(self, records_v) -> None:  # noqa : F811
        """Test length.

        Args:
            records_v : The fixture to obtain records.
        """
        s = RecordsAdapter(records_v)
        # There are three keys : 0, 1, 2
        assert len(s) == 3
        # Add a keys check to ensure mapping works irrespective
        # of typing or collections.abc
        assert len(s.keys()) > 0

    def test_iter(self, records_v) -> None:  # noqa : F811
        """Test iterator.

        Args:
            records_v : The fixture to obtain records.
        """
        s = RecordsAdapter(records_v)
        # There are three keys
        its = iter(s)
        another_its = iter(its)
        assert next(its) == RecordsAdapterKey("System", 0)
        assert next(another_its) == RecordsAdapterKey("System", 1)

        # Test iterator directly via yield
        for idx, k in enumerate(s):
            assert k.sys_id == idx
            assert k.sys_type == "System"

    # FIXME : Typeguard fails with a weird NameError not related to the test.
    @skip_if_env_has("typeguard")
    def test_getitem(self, records_v) -> None:  # noqa : F811
        """Getitem test.

        Args:
            records_v : The fixture to obtain parents.
        """
        s = RecordsAdapter(records_v)

        assert s[RecordsAdapterKey("System", 0)] == SystemRecord(records_v.node, 0)

        def test_key_error(k):
            with pytest.raises(KeyError):
                s[k]
            return True

        incorrect_keys = (
            RecordsAdapterKey("AnotherSystem", 0),  # system name is incorrect
            RecordsAdapterKey("System", 4),
        )  # id is incorrect
        assert all(map(test_key_error, incorrect_keys))


@pytest.fixture
def snap_node() -> Node:
    """Gets node data for a snapshot.

    Returns:
       node with data.
    """
    # TODO : revisit this later on.
    def wrap(x):
        return {"data": x}

    cosserat_rod_records = {
        ElasticaConvention.as_system_key(0): {
            "Position": wrap(2.0),
            "Velocity": wrap(3.0),
            "Curvature": wrap(4.0),
        },
        ElasticaConvention.as_system_key(1): {
            "Position": wrap(4.0),
            "Velocity": wrap(6.0),
            "Curvature": wrap(8.0),
        },
    }
    sphere_records = {
        ElasticaConvention.as_system_key(0): {
            "Position": wrap(1.0),
            "Velocity": wrap(2.0),
        },
        ElasticaConvention.as_system_key(1): {
            "Position": wrap(5.0),
            "Velocity": wrap(8.0),
        },
    }
    return {
        CosseratRodRecordTraits.name(): cosserat_rod_records,
        SphereRecordTraits.name(): sphere_records,
    }


class TestSnapshot:
    """Test snapshot-related functionality."""

    def test_getitem(self, snap_node) -> None:
        """Test getitem.

        Args:
            snap_node : The fixture to obtain node data.
        """
        s = Snapshot(snap_node)

        assert len(s) == 2

        sl = s["CosseratRod"]
        assert isinstance(sl, CosseratRodRecords)
        assert sl == CosseratRodRecords(snap_node["CosseratRod"])

        sl = s["Sphere"]
        assert isinstance(sl, SphereRecords)
        assert sl == SphereRecords(snap_node["Sphere"])

    def test_transforms(self, snap_node) -> None:
        """Test transformation.

        Args:
            snap_node : The fixture to obtain node data.
        """

        def trafo(x):
            return x + 2

        s = Snapshot(snap_node, transforms=trafo)
        sl = s["CosseratRod"]
        assert isinstance(sl, CosseratRodRecords)
        assert sl == CosseratRodRecords(snap_node["CosseratRod"], transforms=trafo)

    def test_iter(self, snap_node) -> None:
        """Test iterator.

        Args:
            snap_node : The fixture to obtain node data.
        """
        s = Snapshot(snap_node)

        # There are two keys
        its = iter(s)
        assert next(its) == "CosseratRod"
        assert next(its) == "Sphere"

        # Test iterator directly via yield
        assert s.keys() == snap_node.keys()

    def test_mixins(self, snap_node) -> None:
        """Test mixins.

        Args:
            snap_node : The fixture to obtain node data.
        """
        s = Snapshot(snap_node)

        sl = s.cosserat_rods()
        assert isinstance(sl, CosseratRodRecords)
        assert sl == CosseratRodRecords(snap_node["CosseratRod"])

        sl = s.spheres()
        assert isinstance(sl, SphereRecords)
        assert sl == SphereRecords(snap_node["Sphere"])

    # FIXME : Typeguard fails with a weird NameError not related to the test.
    @skip_if_env_has("typeguard")
    def test_systems(self, snap_node) -> None:
        """Test systems() call.

        Args:
            snap_node : The fixture to obtain node data.
        """
        s = Snapshot(snap_node)

        sl = s.systems()

        assert len(sl) == 4  # four systems in total
        assert list(map(lambda x: x.sys_id, sl.keys())) == [0, 1, 0, 1]
