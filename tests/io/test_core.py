"""Test cases for core IO."""
from typing import Type

import pytest

from elastica_pipelines.io.core import RecordsAdapter
from elastica_pipelines.io.core import RecordsAdapterKey
from elastica_pipelines.io.core import RecordsIndexedOp
from elastica_pipelines.io.core import RecordsSliceOp
from elastica_pipelines.io.core import SystemRecord
from elastica_pipelines.io.core import SystemRecords
from elastica_pipelines.io.core import SystemRecordsSlice
from elastica_pipelines.io.core import _validate
from elastica_pipelines.io.protocols import ElasticaConvention
from elastica_pipelines.io.typing import Record
from elastica_pipelines.io.typing import RecordsSlice
from tests.io.test_protocols import _Traits
from tests.io.test_protocols import run_traits_error_test
from tests.io.test_protocols import skip_if_env_has


@pytest.fixture
def node_v():
    """Get system record parent for testing."""

    def node_data(x, y):
        return {"k1": {"data": x}, "k2": {"data": y}}

    return {
        ElasticaConvention.as_system_key("0"): node_data(5, 10),
        ElasticaConvention.as_system_key("1"): node_data(20, 40),
        ElasticaConvention.as_system_key("2"): node_data(30, 60),
    }


class TestSystemRecord:
    """Testing SystemRecord."""

    def test_getitem(self, node_v) -> None:
        """Get test.

        Args:
            node_v : The fixture to obtain parents.
        """
        s = SystemRecord(node_v, sys_id=0)
        assert s["k1"] == 5
        assert s["k2"] == 10

        ys = SystemRecord(node_v, sys_id=1)
        assert ys["k1"] == 20
        assert ys["k2"] == 40

    def test_transforms(self, node_v) -> None:
        """Test transformation.

        Args:
            node_v : The fixture to obtain parents.
        """

        def trafo(x):
            return x + 2

        s = SystemRecord(node_v, sys_id=0, transforms=trafo)
        assert s["k1"] == trafo(5)
        assert s["k2"] == trafo(10)

    def test_len(self, node_v) -> None:
        """Test length.

        Args:
            node_v : The fixture to obtain parents.
        """
        s = SystemRecord(node_v, sys_id=0)
        # There are only two keys k1, k2
        assert len(s) == 2
        # Add a keys check to ensure mapping works irrespective
        # of typing or collections.abc
        assert len(s.keys()) > 0

    def test_iter(self, node_v) -> None:
        """Test iterator.

        Args:
            node_v : The fixture to obtain parents.
        """
        s = SystemRecord(node_v, sys_id=0)
        # There are only two keys.
        its = iter(s)
        assert next(its) == "k1"
        assert next(its) == "k2"


class SpecializedTraits(_Traits):
    """Traits class with record and slice specialized for testing."""

    def record_type(self) -> Type[Record]:
        """Obtains type of a (system) record."""
        return SystemRecord

    def slice_type(self) -> Type[RecordsSlice]:
        """Obtains type of (system) records slice."""
        return SystemRecordsSlice

    def name(self) -> str:
        """Obtains the system name."""
        return "System"


class SpecializedRecords(SystemRecords):
    """Specialization of system records."""

    traits = SpecializedTraits()


def test_validate() -> None:
    """Tests index validation."""
    assert _validate(length=20, index=1) == 1
    assert _validate(length=20, index=5) == 5
    assert _validate(length=20, index=-1) == 19
    assert _validate(length=20, index=-5) == 15

    def test_key_raises_error(k):
        with pytest.raises(KeyError):
            _validate(length=20, index=k)

    test_key_raises_error(21)
    test_key_raises_error(-22)


class TestSystemRecords:
    """Testing SystemRecords."""

    def test_len(self, node_v) -> None:
        """Test length.

        Args:
            node_v : The fixture to obtain parents.
        """
        s = SystemRecords(node_v)
        # There are three keys : 100, 200, 300
        assert len(s) == 3
        # Add a keys check to ensure mapping works irrespective
        # of typing or collections.abc
        assert len(s.keys()) > 0

    def test_default_traits(self, node_v) -> None:
        """Test length.

        Args:
            node_v : The fixture to obtain parents.
        """
        s = SystemRecords(node_v)
        run_traits_error_test(s)

    def test_getitem_error(self, node_v) -> None:
        """Getitem error test.

        Args:
            node_v : The fixture to obtain parents.
        """
        s = SystemRecords(node_v)
        match = "system record types"

        def test_key_raises_error(k):
            with pytest.raises(TypeError, match=match):
                s[k]

        # Tests error from the string method
        test_key_raises_error("0")
        test_key_raises_error("1")
        test_key_raises_error("2")
        # Tests error from the int method
        test_key_raises_error(0)
        test_key_raises_error(1)
        test_key_raises_error(2)
        test_key_raises_error(-1)
        # Tests error from the slice method
        test_key_raises_error(slice(None, -1, None))

    def test_iter(self, node_v) -> None:
        """Test iterator.

        Args:
            node_v : The fixture to obtain parents.
        """
        s = SystemRecords(node_v)
        # There are three keys
        its = iter(s)
        assert next(its) == 0
        assert next(its) == 1
        assert next(its) == 2

        # Test iterator directly via yield
        for idx, k in enumerate(s):
            assert k == idx

    def test_getitem(self, node_v) -> None:
        """Getitem error test.

        Args:
            node_v : The fixture to obtain parents.
        """
        s = SpecializedRecords(node_v)

        # Tests the string key
        assert s["0"] == SystemRecord(node_v, 0)
        assert s["1"] == SystemRecord(node_v, 1)
        assert s["2"] == SystemRecord(node_v, 2)

        # Tests the int key
        assert s[0] == SystemRecord(node_v, 0)
        assert s[1] == SystemRecord(node_v, 1)
        assert s[2] == SystemRecord(node_v, 2)

        # Tests the slice method
        sl = slice(None, -1, None)
        actual = s[sl]
        expected = SystemRecordsSlice(s, slice(0, 2, 1))
        assert actual == expected

        # Tests the discrete index method
        sl = [0, 2]
        assert s[sl] == SystemRecordsSlice(s, sl)

    @skip_if_env_has("typeguard")
    def test_getitem_type_error(self, node_v) -> None:
        """Getitem type error test.

        Args:
            node_v : The fixture to obtain parents.
        """

        def test_error(s):
            with pytest.raises(TypeError, match="Invalid argument"):
                s[0.02]
            return True

        records = (SystemRecords(node_v), SpecializedRecords(node_v))
        assert all(map(test_error, records))

    def test_transforms(self, node_v) -> None:
        """Test transformation.

        Args:
            node_v : The fixture to obtain parents.
        """

        def trafo(x):
            return x + 2

        s = SpecializedRecords(node_v, transforms=trafo)
        assert s[0] == SystemRecord(node_v, 0, trafo)


class TestRecordsIndexedOp:
    """Testing Indexed Records Op."""

    def test_get_length_of_slice(self):
        """Tests get_length_of_slice()."""
        dummy_length = 2
        op = RecordsIndexedOp(1)
        assert op.get_length_of_slice(dummy_length) == 1

        op = RecordsIndexedOp([1, 2])
        assert op.get_length_of_slice(dummy_length) == 2

    def test_get_index_into_slice(self):
        """Tests get_index_into_slice()."""
        dummy_length = 2
        op = RecordsIndexedOp(1)
        assert op.get_index_into_slice(0, dummy_length) == 1

        op = RecordsIndexedOp([1, 2, 3])
        assert op.get_index_into_slice(0, dummy_length) == 1
        assert op.get_index_into_slice(1, dummy_length) == 2

        assert op.get_index_into_slice(slice(0, -1, None), dummy_length) == [1, 2]

        assert op.get_index_into_slice([2], dummy_length) == [3]

        def test_error(idx):
            with pytest.raises(IndexError):
                op.get_index_into_slice(idx, dummy_length)
            return True

        error_tests = ([-4], [4], [2, 3])  # , slice(0, 5, 1) : does not raise error
        assert all(map(test_error, error_tests))


class TestRecordsSliceOp:
    """Testing Sliced Records Op."""

    def test_get_length_of_slice(self):
        """Tests get_length_of_slice()."""
        op = RecordsSliceOp(slice(0, 5, 2))
        assert op.get_length_of_slice(10) == 3  # 0, 2, 4
        assert op.get_length_of_slice(3) == 2  # 0, 2

        op = RecordsSliceOp(slice(-4, -1, 2))
        assert op.get_length_of_slice(10) == 2
        assert op.get_length_of_slice(3) == 1

    def test_index_into_slice(self):
        """Tests get_index_into_slice()."""
        op = RecordsSliceOp(slice(0, 5, 2))
        assert op.get_index_into_slice(0, 10) == 0
        assert op.get_index_into_slice(1, 10) == 2
        assert op.get_index_into_slice(2, 10) == 4
        assert op.get_index_into_slice(2, 4) == 4

        assert op.get_index_into_slice([0, 1], 10) == [0, 2]

        op = RecordsSliceOp(slice(0, 10, 2))  # index into original array
        length = op.get_length_of_slice(20)  # parent has t=20 records
        assert op.get_index_into_slice(slice(0, -1, None), length) == slice(0, 8, 2)
        assert op.get_index_into_slice(slice(0, 2, 1), length) == slice(0, 4, 2)
        assert op.get_index_into_slice(slice(0, -1, 2), length) == slice(0, 8, 4)

        def test_error(idx):
            with pytest.raises(KeyError):
                op.get_index_into_slice(idx, length)
            return True

        # length is 5
        error_tests = ([-6], [6], [6, -7])  # , slice(0, 5, 1) : does not raise error
        assert all(map(test_error, error_tests))


@pytest.fixture
def records_v(node_v):
    """Obtains records from node.

    Args:
        node_v : The fixture to obtain node.

    Returns:
        records_v : Specialization of system records.
    """
    return SpecializedRecords(node_v)


class TestSystemRecordsSlice:
    """Testing SystemRecordsSlice."""

    def test_len(self, records_v) -> None:
        """Test length.

        Args:
            records_v : The fixture to obtain records.
        """
        s = records_v[[0, 1]]
        # There are three keys : 100, 200, 300
        assert len(s) == 2
        # Add a keys check to ensure mapping works irrespective
        # of typing or collections.abc
        assert len(s.keys()) > 0

    def test_construction(self, records_v) -> None:
        """Test construction.

        Args:
            records_v : The fixture to obtain records.
        """
        s = records_v[[0, 1]]
        assert len(s) == 2

        s = records_v[:-1]
        assert len(s) == 2

        s = records_v[1:-1]
        assert len(s) == 1

    # def test_traits(self, records_v) -> None:
    #     """Test traits.

    #     Args:
    #         records_v : The fixture to obtain parents.
    #     """
    #     s = records_v[[0, 1]]
    #     assert isinstance(s.traits, SpecializedTraits)

    def test_iter(self, records_v) -> None:
        """Test iterator.

        Args:
            records_v : The fixture to obtain records.
        """
        s = records_v[[1, 2]]
        # There are three keys
        its = iter(s)
        assert next(its) == 0
        assert next(its) == 1

        # Test iterator directly via yield
        for idx, k in enumerate(s):
            assert k == idx

    def test_getitem(self, records_v) -> None:
        """Getitem test.

        Args:
            records_v : The fixture to obtain parents.
        """
        sl = records_v[[1, 2]]

        # Tests the string key
        def test(s):
            assert isinstance(s["0"], SystemRecord)
            assert s["0"].node == records_v.node
            assert s["0"].sys_id == 1
            assert isinstance(s["1"], SystemRecord)
            assert s["1"].node == records_v.node
            assert s["1"].sys_id == 2

        test(sl)

        # Tests the int key
        assert isinstance(sl[0], SystemRecord)
        assert sl[0].node == records_v.node
        assert sl[0].sys_id == 1

        sl = records_v[1:]  # (1, 2)
        # Tests the slice method
        assert sl[:-1] == SystemRecordsSlice(records_v, slice(1, 2, 1))
        test(sl[:])

        # Tests the discrete index method
        test(sl[[0, 1]])

    @skip_if_env_has("typeguard")
    def test_getitem_type_error(self, records_v) -> None:
        """Getitem type error test.

        Args:
            records_v : The fixture to obtain parents.
        """

        def test_error(s):
            with pytest.raises(TypeError, match="Invalid argument"):
                s[0.02]
            return True

        records = (records_v[[0, 1]], records_v[1:2])
        assert all(map(test_error, records))


class TestRecordsAdapter:
    """Testing RecordsAdapter."""

    def test_len(self, records_v) -> None:
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

    def test_iter(self, records_v) -> None:
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

    def test_getitem(self, records_v) -> None:
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
