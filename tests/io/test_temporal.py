"""Test cases for temporal IO types."""
import pytest

from elastica_pipelines.io.core import SystemRecord
from elastica_pipelines.io.temporal import RecordsAdapter
from elastica_pipelines.io.temporal import RecordsAdapterKey
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

    @skip_if_env_has(
        "typeguard"
    )  # Typeguard fails with a weird NameError not related to the test.
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
