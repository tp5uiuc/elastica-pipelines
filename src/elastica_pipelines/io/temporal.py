"""Temporal IO types."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Mapping

from elastica_pipelines.io.core import SystemRecords
from elastica_pipelines.io.protocols import name
from elastica_pipelines.io.typing import RecordLeafs


"""Implementation of snapshot-specific functionality."""


@dataclass(eq=True, frozen=True)
class RecordsAdapterKey:
    """Key containing both the type and id of the system, for iteration."""

    """Type of the system."""
    sys_type: str
    """Unique ID of the system."""
    sys_id: int


class RecordsAdapterIterator:
    """Iterator for adapted records.

    Args:
        records (SystemRecords): Records object being adapted.
    """

    def __init__(self, records: SystemRecords) -> None:  # noqa
        """Initializer."""
        self.records = records
        self.it = iter(records)

    def __iter__(self) -> RecordsAdapterIterator:  # noqa
        return self

    def __next__(self) -> RecordsAdapterKey:  # noqa
        return RecordsAdapterKey(name(self.records), next(self.it))


class RecordsAdapter(Mapping[RecordsAdapterKey, RecordLeafs]):
    """Adapts system-records for system-independent iteration.

    Args:
        records (SystemRecords): Records object being adapted.
    """

    def __init__(self, records: SystemRecords) -> None:  # noqa
        self.records = records

    def __iter__(self) -> RecordsAdapterIterator:  # noqa
        return RecordsAdapterIterator(self.records)

    def __len__(self) -> int:  # noqa
        return len(self.records)

    def __getitem__(self, k: RecordsAdapterKey) -> RecordLeafs:  # noqa
        if k.sys_type is not name(self.records):
            raise KeyError(f"{k.sys_type}")
        return self.records[k.sys_id]
