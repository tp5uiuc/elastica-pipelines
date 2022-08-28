"""Test cases for the __main__ module."""
import pytest

from elastica_pipelines.io.protocols import ElasticaConvention


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
