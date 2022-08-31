"""Test cases for core IO."""
from typing import Type

import pytest

from elastica_pipelines.io.core import SystemRecord
from elastica_pipelines.io.core import SystemRecords
from elastica_pipelines.io.core import _validate
from elastica_pipelines.io.protocols import ElasticaConvention
from elastica_pipelines.io.typing import Record
from elastica_pipelines.io.typing import RecordsSlice
from tests.io.test_protocols import _Traits
from tests.io.test_protocols import run_traits_error_test
from tests.io.test_protocols import skip_if_env_has


@pytest.fixture
def parent_v():
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

    def test_getitem(self, parent_v) -> None:
        """Get test.

        Args:
            parent_v : The fixture to obtain parents.
        """
        s = SystemRecord(parent_v, sys_id=0)
        assert s["k1"] == 5
        assert s["k2"] == 10

        ys = SystemRecord(parent_v, sys_id=1)
        assert ys["k1"] == 20
        assert ys["k2"] == 40

    def test_transforms(self, parent_v) -> None:
        """Test transformation.

        Args:
            parent_v : The fixture to obtain parents.
        """

        def trafo(x):
            return x + 2

        s = SystemRecord(parent_v, sys_id=0, transforms=trafo)
        assert s["k1"] == trafo(5)
        assert s["k2"] == trafo(10)

    def test_len(self, parent_v) -> None:
        """Test length.

        Args:
            parent_v : The fixture to obtain parents.
        """
        s = SystemRecord(parent_v, sys_id=0)
        # There are only two keys k1, k2
        assert len(s) == 2
        # Add a keys check to ensure mapping works irrespective
        # of typing or collections.abc
        assert len(s.keys()) > 0

    def test_iter(self, parent_v) -> None:
        """Test iterator.

        Args:
            parent_v : The fixture to obtain parents.
        """
        s = SystemRecord(parent_v, sys_id=0)
        # There are only two keys.
        its = iter(s)
        assert next(its) == "k1"
        assert next(its) == "k2"


class _Sink(RecordsSlice):
    def __init__(self, *args, **kwargs) -> None:  # noqa
        self.args = args
        self.kwargs = kwargs

    def __iter__(self):  # noqa
        ...  # pragma: no cover

    def __len__(self) -> int:  # noqa
        ...  # pragma: no cover

    def __getitem__(self, k):  # noqa
        ...  # pragma: no cover


class SpecializedTraits(_Traits):
    """Traits class with record and slice specialized for testing."""

    def record_type(self) -> Type[Record]:
        """Obtains type of a (system) record."""
        return SystemRecord

    def slice_type(self) -> Type[RecordsSlice]:
        """Obtains type of (system) records slice."""
        return _Sink


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

    def test_len(self, parent_v) -> None:
        """Test length.

        Args:
            parent_v : The fixture to obtain parents.
        """
        s = SystemRecords(parent_v)
        # There are three keys : 100, 200, 300
        assert len(s) == 3
        # Add a keys check to ensure mapping works irrespective
        # of typing or collections.abc
        assert len(s.keys()) > 0

    def test_default_traits(self, parent_v) -> None:
        """Test length.

        Args:
            parent_v : The fixture to obtain parents.
        """
        s = SystemRecords(parent_v)
        run_traits_error_test(s)

    def test_getitem_error(self, parent_v) -> None:
        """Getitem error test.

        Args:
            parent_v : The fixture to obtain parents.
        """
        s = SystemRecords(parent_v)
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

    def test_iter(self, parent_v) -> None:
        """Test iterator.

        Args:
            parent_v : The fixture to obtain parents.
        """
        s = SystemRecords(parent_v)
        # There are three keys
        its = iter(s)
        assert next(its) == 0
        assert next(its) == 1
        assert next(its) == 2

        # Test iterator directly via yield
        for idx, k in enumerate(s):
            assert k == idx

    def test_getitem(self, parent_v) -> None:
        """Getitem error test.

        Args:
            parent_v : The fixture to obtain parents.
        """
        s = SpecializedRecords(parent_v)

        # Tests the string key
        assert s["0"] == SystemRecord(parent_v, 0)
        assert s["1"] == SystemRecord(parent_v, 1)
        assert s["2"] == SystemRecord(parent_v, 2)

        # Tests the int key
        assert s[0] == SystemRecord(parent_v, 0)
        assert s[1] == SystemRecord(parent_v, 1)
        assert s[2] == SystemRecord(parent_v, 2)

        # Tests the slice method
        # TODO : update with proper slice method
        sl = slice(None, -1, None)
        sliced = s[sl]
        assert type(sliced) == _Sink
        assert sliced.args == (s, slice(*sl.indices(3)))

    @skip_if_env_has("typeguard")
    def test_getitem_type_error(self, parent_v) -> None:
        """Getitem type error test.

        Args:
            parent_v : The fixture to obtain parents.
        """

        def test_error(s):
            with pytest.raises(TypeError, match="Invalid argument"):
                s[0.02]
            return True

        records = (SystemRecords(parent_v), SpecializedRecords(parent_v))
        assert all(map(test_error, records))

    def test_transforms(self, parent_v) -> None:
        """Test transformation.

        Args:
            parent_v : The fixture to obtain parents.
        """

        def trafo(x):
            return x + 2

        s = SpecializedRecords(parent_v, transforms=trafo)
        assert s[0] == SystemRecord(parent_v, 0, trafo)
