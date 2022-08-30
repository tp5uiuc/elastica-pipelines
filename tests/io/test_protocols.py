"""Test cases for IO protocols."""
import os
from typing import Type

import pytest

from elastica_pipelines.io.protocols import ElasticaConvention
from elastica_pipelines.io.protocols import SystemIndex
from elastica_pipelines.io.typing import ConcreteRecord
from elastica_pipelines.io.typing import Record
from elastica_pipelines.io.typing import Records
from elastica_pipelines.io.typing import RecordsSlice


class TestElasticaConvention:
    """Tests Elastica convention."""

    @pytest.mark.parametrize("arg_type", [int, str])
    def test_as_system_key(self, arg_type):
        """Test system key."""
        fun = ElasticaConvention.as_system_key
        assert fun(arg_type(10)) == "0000000010"
        assert fun(arg_type(100)) == "0000000100"
        assert fun(arg_type(1000)) == "0000001000"

    @pytest.mark.parametrize("arg_type", [int, str])
    def test_as_record_key(self, arg_type):
        """Test record key."""
        fun = ElasticaConvention.as_record_key
        assert fun(arg_type(10)) == "000010"
        assert fun(arg_type(100)) == "000100"
        assert fun(arg_type(1000)) == "001000"

    def test_access(self):
        """Test access."""
        fun = ElasticaConvention.access
        assert fun({"data": 2}) == 2
        assert fun({"data": 20, "mark": 4}) == 20


class _Traits:
    def __init__(self) -> None:
        pass

    def record_type(self) -> Type[Record]:
        """Obtains type of a (system) record."""
        return dict

    def records_type(self) -> Type[Records[ConcreteRecord]]:
        """Obtains type of (system) records."""
        return dict

    def slice_type(self) -> Type[RecordsSlice[ConcreteRecord]]:
        """Obtains type of (system) records slice."""
        return dict

    def name(self) -> str:
        """Obtains the system name."""
        return "_Traits"

    def index_type(self) -> Type[SystemIndex]:
        """Obtains type of (system) index."""
        return SystemIndex


def skip_if_env_has(*envs):
    """Skip a test if an environment variable is found."""
    env = os.environ.get("ENVIRONMENT", "test")

    envs = envs if isinstance(envs, list) else [*envs]

    return pytest.mark.skipif(
        env in envs, reason=f"Not suitable envrionment {env} for current test"
    )


class TestTraits:
    """Tests Traits free function."""

    class _HasTraits:
        traits = _Traits()

        def __init__(self) -> None:
            pass

    @skip_if_env_has("typeguard")
    @pytest.mark.parametrize("arg_type", [_HasTraits, _HasTraits()])
    def test_record_type(self, arg_type):
        """Test record type."""
        from elastica_pipelines.io.protocols import record_type as fun

        assert fun(arg_type) == dict

    @skip_if_env_has("typeguard")
    @pytest.mark.parametrize("arg_type", [_HasTraits, _HasTraits()])
    def test_records_type(self, arg_type):
        """Test records type."""
        from elastica_pipelines.io.protocols import records_type as fun

        assert fun(arg_type) == dict

    @skip_if_env_has("typeguard")
    @pytest.mark.parametrize("arg_type", [_HasTraits, _HasTraits()])
    def test_slice_type(self, arg_type):
        """Test slice type."""
        from elastica_pipelines.io.protocols import slice_type as fun

        assert fun(arg_type) == dict

    @skip_if_env_has("typeguard")
    @pytest.mark.parametrize("arg_type", [_HasTraits, _HasTraits()])
    def test_name_type(self, arg_type):
        """Test name ."""
        from elastica_pipelines.io.protocols import name as fun

        assert fun(arg_type) == "_Traits"

    @skip_if_env_has("typeguard")
    @pytest.mark.parametrize("arg_type", [_HasTraits, _HasTraits()])
    def test_index_type(self, arg_type):
        """Test index type."""
        from elastica_pipelines.io.protocols import index_type as fun

        assert fun(arg_type) == SystemIndex
