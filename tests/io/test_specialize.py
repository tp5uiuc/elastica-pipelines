"""Test cases for IO specializations."""

from typing import Type

from elastica_pipelines.io.protocols import RecordTraits
from elastica_pipelines.io.protocols import index_type
from elastica_pipelines.io.protocols import name
from elastica_pipelines.io.protocols import record_type
from elastica_pipelines.io.protocols import records_type
from elastica_pipelines.io.protocols import slice_type
from elastica_pipelines.io.specialize import CosseratRodRecordTraits


def run_traits_presence_test(t: Type[RecordTraits]):
    """Tests presence of traits class recursively."""
    funs = (record_type, records_type, slice_type, index_type)

    class A:
        traits = t

    def test_traits(fun):
        """Runner to tests traits."""
        assert fun(A).traits == t
        return True

    assert all(map(test_traits, funs))

    assert name(A)


class TestCosseratRodTraits:
    """Tests CosseratRod Traits."""

    def test_traits_presence(self):
        """Test presence of traits class in all CosseratRod specializations."""
        traits = CosseratRodRecordTraits
        run_traits_presence_test(traits)
