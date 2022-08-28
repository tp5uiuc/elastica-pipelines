"""Elastica IO protocols."""
from __future__ import annotations

from typing import Any

from typing_extensions import Protocol

from .typing import Index
from .typing import Key
from .typing import Node
from .typing import Record
from .typing import Records
from .typing import RecordsSlice


class ElasticaConvention:
    """Customization point for internal Elastica++ convention.

    Supports only static methods since this is not purposed for change
    by the user.
    """

    @staticmethod
    def len_system_key() -> int:
        """Length of a system key used internally by Elastica++."""
        return 10

    @staticmethod
    def as_system_key(k: Key) -> str:
        """Converts a system key to the format used internally by Elastica++.

        Args:
            k: Key to be converted.

        Returns:
            Formatted system key.
        """
        return str(k).zfill(ElasticaConvention.len_system_key())

    @staticmethod
    def len_record_key() -> int:
        """Length of a record key used internally by Elastica++."""
        return 6

    @staticmethod
    def as_record_key(k: Key) -> str:
        """Converts a record key to the format used internally by Elastica++.

        Args:
            k: Key to be converted.

        Returns:
            Formatted record key.
        """
        return str(k).zfill(ElasticaConvention.len_record_key())

    @staticmethod
    def access(n: Node) -> Any:
        """Access data from a node, per Elastica++ convention.

        Args:
            n: Node to access data from.

        Returns:
            Data from node
        """
        return n["data"]


class RecordTraits(Protocol):
    """Protocol for a data-record trait instance.

    A trait class is intended to customize record behavior for
    different Elastica++ systems.
    """

    def record_type(self) -> type[Record]:
        """Obtains type of a (system) record."""
        ...  # pragma: no cover

    def records_type(self) -> type[Records]:
        """Obtains type of (system) records."""
        ...  # pragma: no cover

    def slice_type(self) -> type[RecordsSlice]:
        """Obtains type of (system) records slice."""
        ...  # pragma: no cover

    def name(self) -> str:
        """Obtains the system name."""
        ...  # pragma: no cover

    def index_type(self) -> type[SystemIndex]:
        """Obtains type of (system) index."""
        ...  # pragma: no cover


class HasRecordTraits(Protocol):
    """Protocol for records.

    Each record type is expected to implement this Protocol.
    """

    traits: RecordTraits


class SystemIndex(HasRecordTraits):
    """Protocol for index into data-records."""

    index: Index
