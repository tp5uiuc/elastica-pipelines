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


# Defines cosserat-rod records
class CosseratRodWithoutDampingRecord(SystemRecord):
    """CosseratRodWithoutDamping record type."""

    traits: ClassVar[Type[RecordTraits]]


class CosseratRodWithoutDampingRecords(SystemRecords):
    """CosseratRodWithoutDamping records type."""

    traits: ClassVar[Type[RecordTraits]]


class CosseratRodWithoutDampingRecordsSlice(SystemRecordsSlice):
    """CosseratRodWithoutDamping records slice type."""

    traits: ClassVar[Type[RecordTraits]]


@dataclass(eq=True, frozen=True)
class CosseratRodWithoutDampingRecordIndex(SystemIndices):
    """CosseratRodWithoutDamping record index type."""

    indices: Indices
    traits: ClassVar[Type[RecordTraits]]


class CosseratRodWithoutDampingRecordTraits(RecordTraits):
    """Traits class for CosseratRodWithoutDamping records."""

    @staticmethod
    def record_type() -> Type[CosseratRodWithoutDampingRecord]:
        """Obtains type of a (system) record."""
        return CosseratRodWithoutDampingRecord

    @staticmethod
    def records_type() -> Type[CosseratRodWithoutDampingRecords]:
        """Obtains type of (system) records."""
        return CosseratRodWithoutDampingRecords

    @staticmethod
    def slice_type() -> Type[CosseratRodWithoutDampingRecordsSlice]:
        """Obtains type of (system) records slice."""
        return CosseratRodWithoutDampingRecordsSlice

    @staticmethod
    def name() -> str:
        """Obtains the name."""
        return "CosseratRodWithoutDamping"

    @staticmethod
    def index_type() -> Type[CosseratRodWithoutDampingRecordIndex]:
        """Obtains type of (system) index."""
        return CosseratRodWithoutDampingRecordIndex


CosseratRodWithoutDampingRecord.traits = CosseratRodWithoutDampingRecordTraits
CosseratRodWithoutDampingRecords.traits = CosseratRodWithoutDampingRecordTraits
CosseratRodWithoutDampingRecordsSlice.traits = CosseratRodWithoutDampingRecordTraits
CosseratRodWithoutDampingRecordIndex.traits = CosseratRodWithoutDampingRecordTraits


# Defines sphere records
class SphereRecord(SystemRecord):
    """Sphere record type."""

    traits: ClassVar[Type[RecordTraits]]


class SphereRecords(SystemRecords):
    """Sphere records type."""

    traits: ClassVar[Type[RecordTraits]]


class SphereRecordsSlice(SystemRecordsSlice):
    """Sphere records slice type."""

    traits: ClassVar[Type[RecordTraits]]


@dataclass(eq=True, frozen=True)
class SphereRecordIndex(SystemIndices):
    """Sphere record index type."""

    indices: Indices
    traits: ClassVar[Type[RecordTraits]]


class SphereRecordTraits(RecordTraits):
    """Traits class for Sphere records."""

    @staticmethod
    def record_type() -> Type[SphereRecord]:
        """Obtains type of a (system) record."""
        return SphereRecord

    @staticmethod
    def records_type() -> Type[SphereRecords]:
        """Obtains type of (system) records."""
        return SphereRecords

    @staticmethod
    def slice_type() -> Type[SphereRecordsSlice]:
        """Obtains type of (system) records slice."""
        return SphereRecordsSlice

    @staticmethod
    def name() -> str:
        """Obtains the name."""
        return "Sphere"

    @staticmethod
    def index_type() -> Type[SphereRecordIndex]:
        """Obtains type of (system) index."""
        return SphereRecordIndex


SphereRecord.traits = SphereRecordTraits
SphereRecords.traits = SphereRecordTraits
SphereRecordsSlice.traits = SphereRecordTraits
SphereRecordIndex.traits = SphereRecordTraits
