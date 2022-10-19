"""Test cases for temporal IO types."""
from dataclasses import dataclass
from typing import Any
from typing import Dict
from typing import Tuple

import pytest

from elastica_pipelines.io.core import SystemRecord
from elastica_pipelines.io.protocols import ElasticaConvention
from elastica_pipelines.io.specialize import CosseratRodRecord
from elastica_pipelines.io.specialize import CosseratRodRecordIndex
from elastica_pipelines.io.specialize import CosseratRodRecords
from elastica_pipelines.io.specialize import CosseratRodRecordsSlice
from elastica_pipelines.io.specialize import CosseratRodRecordTraits
from elastica_pipelines.io.specialize import CosseratRodWithoutDampingRecord
from elastica_pipelines.io.specialize import CosseratRodWithoutDampingRecordIndex
from elastica_pipelines.io.specialize import CosseratRodWithoutDampingRecords
from elastica_pipelines.io.specialize import CosseratRodWithoutDampingRecordsSlice
from elastica_pipelines.io.specialize import CosseratRodWithoutDampingRecordTraits
from elastica_pipelines.io.specialize import SphereRecord
from elastica_pipelines.io.specialize import SphereRecordIndex
from elastica_pipelines.io.specialize import SphereRecords
from elastica_pipelines.io.specialize import SphereRecordsSlice
from elastica_pipelines.io.specialize import SphereRecordTraits
from elastica_pipelines.io.temporal import RecordsAdapter
from elastica_pipelines.io.temporal import RecordsAdapterKey
from elastica_pipelines.io.temporal import Series
from elastica_pipelines.io.temporal import SeriesKey
from elastica_pipelines.io.temporal import SeriesSelection
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
        ElasticaConvention.as_system_key(2): {
            "Position": wrap(6.0),
            "Velocity": wrap(9.0),
            "Curvature": wrap(12.0),
        },
    }
    cosserat_rod_without_damping_records = {
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
        ElasticaConvention.as_system_key(2): {
            "Position": wrap(6.0),
            "Velocity": wrap(9.0),
            "Curvature": wrap(12.0),
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
        CosseratRodWithoutDampingRecordTraits.name(): cosserat_rod_without_damping_records,  # noqa : B950
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

        assert len(s) == 3

        sl = s["CosseratRod"]
        assert isinstance(sl, CosseratRodRecords)
        assert sl == CosseratRodRecords(snap_node["CosseratRod"])

        sl = s["CosseratRodWithoutDamping"]
        assert isinstance(sl, CosseratRodWithoutDampingRecords)
        assert sl == CosseratRodWithoutDampingRecords(
            snap_node["CosseratRodWithoutDamping"]
        )

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
        assert next(its) == "CosseratRodWithoutDamping"
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

        sl = s.cosserat_rods_without_damping()
        assert isinstance(sl, CosseratRodWithoutDampingRecords)
        assert sl == CosseratRodWithoutDampingRecords(
            snap_node["CosseratRodWithoutDamping"]
        )

        sl = s.spheres()
        assert isinstance(sl, SphereRecords)
        assert sl == SphereRecords(snap_node["Sphere"])

    # FIXME : Typeguard fails with a weird NameError not related to the test.
    @skip_if_env_has("typeguard")
    def test_rods(self, snap_node) -> None:
        """Test rods() call.

        Args:
            snap_node : The fixture to obtain node data.
        """
        s = Snapshot(snap_node)

        sl = s.rods()

        assert len(sl) == (3 + 3)  # Two cosserat rod types
        assert list(map(lambda x: x.sys_id, sl.keys())) == [0, 1, 2, 0, 1, 2]

    # FIXME : Typeguard fails with a weird NameError not related to the test.
    @skip_if_env_has("typeguard")
    def test_systems(self, snap_node) -> None:
        """Test systems() call.

        Args:
            snap_node : The fixture to obtain node data.
        """
        s = Snapshot(snap_node)

        sl = s.systems()

        assert len(sl) == (2 + 3 + 3)  # Sphere + Two cosserat rods
        assert list(map(lambda x: x.sys_id, sl.keys())) == [0, 1, 0, 1, 2, 0, 1, 2]


@dataclass
class WrappedFloat:
    """Wraps a scalar float with a HDF5 style getitem access."""

    value: float

    def __getitem__(self, key: Tuple[Any, ...]) -> float:  # noqa
        return self.value


def temporal_information(it: int) -> Dict[str, Dict[str, WrappedFloat]]:
    """Construct temporal information."""
    return {"TimeMetadata": {"time": WrappedFloat(it * 0.1), "dt": WrappedFloat(0.02)}}


@pytest.fixture
def series_node(snap_node) -> Node:
    """Gets node data for a snapshot.

    Returns:
       node with data.
    """

    def prepare_node(it: int) -> Node:
        return {
            ElasticaConvention.as_record_key(it): dict(
                **{"data": snap_node}, **temporal_information(it)
            )
        }

    return dict(
        **prepare_node(50), **dict(prepare_node(100), **dict(prepare_node(150)))
    )


class TestSeries:
    """Test series-related functionality."""

    def test_getitem(self, series_node) -> None:
        """Test getitem.

        Args:
            series_node : The fixture to obtain series node data.
        """
        s = Series(series_node)

        assert len(s) == 3

        sl = s[50]
        assert isinstance(sl, Snapshot)
        assert sl == Snapshot(series_node["000050"]["data"])

        sl = s[100]
        assert isinstance(sl, Snapshot)
        assert sl == Snapshot(series_node["000100"]["data"])

        # Getitem test with SeriesKey
        k = SeriesKey(100, 10.0, 0.02)
        sl = s[k]
        assert isinstance(sl, Snapshot)
        assert sl == Snapshot(series_node["000100"]["data"])

    def test_transforms(self, series_node) -> None:
        """Test transformation.

        Args:
            series_node : The fixture to obtain series node data.
        """

        def trafo(x):
            return x + 2

        s = Series(series_node, transforms=trafo)

        sl = s[50]
        assert isinstance(sl, Snapshot)
        assert sl == Snapshot(series_node["000050"]["data"], transforms=trafo)

    # FIXME : Typeguard fails with a weird NameError not related to the test.
    @skip_if_env_has("typeguard")
    def test_iter(self, series_node) -> None:
        """Test iterator.

        Args:
            series_node : The fixture to obtain series node data.
        """
        s = Series(series_node)

        # There are two keys
        its = iter(s)
        assert next(its) == SeriesKey(50, 5.0, 0.02)
        assert next(its) == SeriesKey(100, 10.0, 0.02)
        assert next(its) == SeriesKey(150, 15.0, 0.02)
        assert iter(its) == its

    # FIXME : Typeguard fails with a weird NameError not related to the test.
    @skip_if_env_has("typeguard")
    def test_iterations(self, series_node) -> None:
        """Test iterations/items.

        Args:
            series_node : The fixture to obtain series node data.
        """
        s = Series(series_node)

        for t, snaps in s.iterations():
            assert t.dt == 0.02
            TestSnapshot().test_getitem(snaps.node)
            TestSnapshot().test_iter(snaps.node)
            TestSnapshot().test_mixins(snaps.node)
            # TestSnapshot().test_systems(snaps.node)


class TestSeriesSelection:
    """Test series selection-related functionality."""

    # FIXME : Typeguard fails with a weird NameError not related to the test.
    @skip_if_env_has("typeguard")
    def test_getitem(self, series_node) -> None:
        """Test getitem.

        Args:
            series_node : The fixture to obtain series node data.
        """
        s = Series(series_node)
        sel = s.temporal_select(CosseratRodRecordIndex(0))

        # temporal
        assert len(sel) == 3

        sl = sel[50]
        assert isinstance(sl, CosseratRodRecord)
        assert sl == CosseratRodRecord(series_node["000050"]["data"]["CosseratRod"], 0)

        # Test without damping
        sel = s.temporal_select(CosseratRodWithoutDampingRecordIndex([0, 1]))

        # temporal
        assert len(sel) == 3

        sl = sel[50]
        assert isinstance(sl, CosseratRodWithoutDampingRecordsSlice)
        assert sl[0] == CosseratRodWithoutDampingRecord(
            series_node["000050"]["data"]["CosseratRodWithoutDamping"], 0
        )
        assert sl[1] == CosseratRodWithoutDampingRecord(
            series_node["000050"]["data"]["CosseratRodWithoutDamping"], 1
        )

        sel = s.temporal_select(CosseratRodRecordIndex([1, 2]))

        # temporal
        assert len(sel) == 3

        sl = sel[50]
        assert isinstance(sl, CosseratRodRecordsSlice)

        assert sl[0] == CosseratRodRecord(
            series_node["000050"]["data"]["CosseratRod"], 1
        )
        assert sl[1] == CosseratRodRecord(
            series_node["000050"]["data"]["CosseratRod"], 2
        )

        def test_index_error(k):
            with pytest.raises(IndexError):
                sl[k]
            return True

        incorrect_indices = (2, 3, 4)
        assert all(map(test_index_error, incorrect_indices))

        sel = s.temporal_select(SphereRecordIndex(slice(None, -1, None)))
        # temporal
        assert len(sel) == 3
        sl = sel[50]
        assert isinstance(sl, SphereRecordsSlice)
        assert sl[0] == SphereRecord(series_node["000050"]["data"]["Sphere"], 0)

        def test_key_error(k):
            with pytest.raises(KeyError):
                sl[k]
            return True

        incorrect_keys = incorrect_indices
        assert all(map(test_key_error, incorrect_keys))

    # FIXME : Typeguard fails with a weird NameError not related to the test.
    @skip_if_env_has("typeguard")
    def test_iter(self, series_node) -> None:
        """Test iterator.

        Args:
            series_node : The fixture to obtain series node data.
        """
        series = Series(series_node)
        s = series.temporal_select(CosseratRodRecordIndex([1, 2]))

        # There are two keys
        its = iter(s)
        assert next(its) == SeriesKey(50, 5.0, 0.02)
        assert next(its) == SeriesKey(100, 10.0, 0.02)
        assert next(its) == SeriesKey(150, 15.0, 0.02)
        assert iter(its) == its

    # FIXME : Typeguard fails with a weird NameError not related to the test.
    @skip_if_env_has("typeguard")
    def test_iterations(self, series_node) -> None:
        """Test iterations/items.

        Args:
            series_node : The fixture to obtain series node data.
        """
        series = Series(series_node)
        s = series.temporal_select(CosseratRodRecordIndex(1))

        for t, rod in s.iterations():
            assert t.dt == 0.02
            assert rod["Position"] == 4.0

    # FIXME : Typeguard fails with a weird NameError not related to the test.
    @skip_if_env_has("typeguard")
    def test_temporal_select(self, series_node) -> None:
        """Test iterations/items.

        Args:
            series_node : The fixture to obtain series node data.
        """
        series = Series(series_node)
        # Selects the slice (1, 2)
        s = series.temporal_select(CosseratRodRecordIndex(slice(1, None, None)))
        assert len(s) == 3

        def test_type_error(k):
            with pytest.raises(TypeError, match="does not match"):
                s.temporal_select(k)
            return True

        assert all(
            map(
                test_type_error,
                (
                    SphereRecordIndex(0),
                    SphereRecordIndex([0, 1]),
                    SphereRecordIndex(slice(None, -1, None)),
                ),
            )
        )

        # Selects 1
        sel = s.temporal_select(CosseratRodRecordIndex(0))
        assert len(sel) == 3
        assert isinstance(sel, SeriesSelection)

        sl = sel[50]
        assert sl == CosseratRodRecord(series_node["000050"]["data"]["CosseratRod"], 1)

        # Selects 0, 1
        sel = s.temporal_select(CosseratRodRecordIndex([0, 1]))
        assert len(sel) == 3
        assert isinstance(sel, SeriesSelection)

        sl = sel[50]
        assert sl[0] == CosseratRodRecord(
            series_node["000050"]["data"]["CosseratRod"], 1
        )
        assert sl[1] == CosseratRodRecord(
            series_node["000050"]["data"]["CosseratRod"], 2
        )

        # Selects slice(0, 1)
        sel = s.temporal_select(CosseratRodRecordIndex(slice(None, None, None)))
        assert len(sel) == 3
        assert isinstance(sel, SeriesSelection)

        sl = sel[50]
        assert sl[0] == CosseratRodRecord(
            series_node["000050"]["data"]["CosseratRod"], 1
        )
        assert sl[1] == CosseratRodRecord(
            series_node["000050"]["data"]["CosseratRod"], 2
        )
