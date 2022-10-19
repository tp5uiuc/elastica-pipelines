"""Elastica IO protocols."""
from __future__ import annotations

from typing import Any
from typing import ClassVar
from typing import NoReturn
from typing import Type

from typing_extensions import Protocol

from elastica_pipelines.io.typing import Indices
from elastica_pipelines.io.typing import Key
from elastica_pipelines.io.typing import Node
from elastica_pipelines.io.typing import Record
from elastica_pipelines.io.typing import Records
from elastica_pipelines.io.typing import RecordsSlice


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
        return 10

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


class BackendAccess(Protocol):
    """Protocol for backend-dependent data access."""

    @staticmethod
    def access_time(n: Node) -> float:  # noqa
        ...  # pragma: no cover

    @staticmethod
    def access_dt(n: Node) -> float:  # noqa
        ...  # pragma: no cover

    @staticmethod
    def access_data(n: Node) -> Any:  # noqa
        ...  # pragma: no cover


class RecordTraits(Protocol):
    """Protocol for a data-record trait instance.

    A trait class is intended to customize record behavior for
    different Elastica++ systems.
    """

    @staticmethod
    def record_type() -> Type[Record]:
        """Obtains type of a (system) record."""
        ...  # pragma: no cover

    @staticmethod
    def records_type() -> Type[Records]:
        """Obtains type of (system) records."""
        ...  # pragma: no cover

    @staticmethod
    def slice_type() -> Type[RecordsSlice]:
        """Obtains type of (system) records slice."""
        ...  # pragma: no cover

    @staticmethod
    def name() -> str:
        """Obtains the system name."""
        ...  # pragma: no cover

    @staticmethod
    def index_type() -> Type[SystemIndices]:
        """Obtains type of (system) index."""
        ...  # pragma: no cover


class HasRecordTraits(Protocol):
    """Protocol for records.

    Each record type is expected to implement this Protocol.
    """

    traits: ClassVar[Type[RecordTraits]]


class _ErrorOutTraits:
    """Trait that always publishes an error message.

    Meets the ``RecordTraits`` protocol
    """

    @staticmethod
    def raise_error() -> NoReturn:
        """Raises user error for accessing raw system record types.

        Raises:
            TypeError: For accessing types that are not meant to be accessed.
        """
        raise TypeError(
            "Raw system record types are not meant to be accessed."
            "They must be specialized with a custom traits class first."
        )

    @staticmethod
    def record_type() -> Type[Record]:
        """Obtains type of a (system) record."""
        return _ErrorOutTraits.raise_error()

    @staticmethod
    def records_type() -> Type[Records]:
        """Obtains type of (system) records."""
        return _ErrorOutTraits.raise_error()

    @staticmethod
    def slice_type() -> Type[RecordsSlice]:
        """Obtains type of (system) records slice."""
        return _ErrorOutTraits.raise_error()

    @staticmethod
    def name() -> str:
        """Obtains the system name."""
        _ErrorOutTraits.raise_error()

    @staticmethod
    def index_type() -> Type[SystemIndices]:
        """Obtains type of (system) index."""
        return _ErrorOutTraits.raise_error()


def record_type(x: HasRecordTraits) -> Type[Record]:
    """Obtain type of a (system) record.

    Args:
        x: conforming to the HasRecordTraits protocol

    Returns:
        Record type
    """
    return x.traits.record_type()


def records_type(x: HasRecordTraits) -> Type[Records]:
    """Obtain type of (system) records.

    Args:
        x: conforming to the HasRecordTraits protocol

    Returns:
        Records type
    """
    return x.traits.records_type()


def slice_type(x: HasRecordTraits) -> Type[RecordsSlice]:
    """Obtain type of (system) records slice.

    Args:
        x: conforming to the HasRecordTraits protocol

    Returns:
        Record slice type
    """
    return x.traits.slice_type()


def name(x: HasRecordTraits) -> str:
    """Obtains the system name.

    Args:
        x: conforming to the HasRecordTraits protocol

    Returns:
        Name of the system
    """
    return x.traits.name()


def index_type(x: HasRecordTraits) -> Type[SystemIndices]:
    """Obtains the type of (system) index.

    Args:
        x: conforming to the HasRecordTraits protocol

    Returns:
        System index type.
    """
    return x.traits.index_type()


class SystemIndices(HasRecordTraits):
    """Protocol for index into data-records."""

    indices: Indices
    traits: ClassVar[Type[RecordTraits]]

    def __init__(self, indices: Indices) -> None:  # noqa
        ...  # pragma: no cover
