"""Specialization for Elastica++ types."""

from dataclasses import dataclass
from typing import ClassVar
from typing import Type

from elastica_pipelines.io.core import SystemRecord
from elastica_pipelines.io.core import SystemRecords
from elastica_pipelines.io.core import SystemRecordsSlice
from elastica_pipelines.io.protocols import RecordTraits
from elastica_pipelines.io.protocols import SystemIndices
from elastica_pipelines.io.typing import Indices


# Defines cosserat-rod records
class CosseratRodRecord(SystemRecord):
    """CosseratRod record type."""

    traits: ClassVar[Type[RecordTraits]]


class CosseratRodRecords(SystemRecords):
    """CosseratRod records type."""

    traits: ClassVar[Type[RecordTraits]]


class CosseratRodRecordsSlice(SystemRecordsSlice):
    """CosseratRod records slice type."""

    traits: ClassVar[Type[RecordTraits]]


@dataclass(eq=True, frozen=True)
class CosseratRodRecordIndex(SystemIndices):
    """CosseratRod record index type."""

    indices: Indices
    traits: ClassVar[Type[RecordTraits]]


class CosseratRodRecordTraits(RecordTraits):
    """Traits class for CosseratRod records."""

    @staticmethod
    def record_type() -> Type[CosseratRodRecord]:
        """Obtains type of a (system) record."""
        return CosseratRodRecord

    @staticmethod
    def records_type() -> Type[CosseratRodRecords]:
        """Obtains type of (system) records."""
        return CosseratRodRecords

    @staticmethod
    def slice_type() -> Type[CosseratRodRecordsSlice]:
        """Obtains type of (system) records slice."""
        return CosseratRodRecordsSlice

    @staticmethod
    def name() -> str:
        """Obtains the name."""
        return "CosseratRod"

    @staticmethod
    def index_type() -> Type[CosseratRodRecordIndex]:
        """Obtains type of (system) index."""
        return CosseratRodRecordIndex


CosseratRodRecord.traits = CosseratRodRecordTraits
CosseratRodRecords.traits = CosseratRodRecordTraits
CosseratRodRecordsSlice.traits = CosseratRodRecordTraits
CosseratRodRecordIndex.traits = CosseratRodRecordTraits
