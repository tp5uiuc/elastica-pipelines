"""Temporal IO types."""
from __future__ import annotations

from collections.abc import Iterator
from dataclasses import dataclass
from typing import Any
from typing import ChainMap
from typing import Dict
from typing import Mapping
from typing import Optional
from typing import Type

from typing_extensions import Protocol
from typing_extensions import TypeAlias

from elastica_pipelines.io.core import SystemRecords
from elastica_pipelines.io.protocols import name
from elastica_pipelines.io.specialize import CosseratRodRecords
from elastica_pipelines.io.specialize import CosseratRodRecordTraits
from elastica_pipelines.io.specialize import SphereRecords
from elastica_pipelines.io.specialize import SphereRecordTraits
from elastica_pipelines.io.typing import FuncType
from elastica_pipelines.io.typing import Node
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


class HasGetItem(Protocol):
    """Get item protocol."""

    def __getitem__(self, k: str) -> Any:  # noqa
        ...  # pragma: no cover


class CosseratRodRecordsMixin:
    """Mixin for cosserat_rods() access."""

    def cosserat_rods(self: HasGetItem) -> CosseratRodRecords:
        """Access cosserat rod records.

        Returns:
            CosseratRod records.
        """
        return self.__getitem__(CosseratRodRecordTraits.name())


class SphereRecordsMixin:
    """Mixin for spheres() access."""

    def spheres(self: HasGetItem) -> SphereRecords:
        """Access sphere records.

        Returns:
            Sphere records.
        """
        return self.__getitem__(SphereRecordTraits.name())


RecordsMap: TypeAlias = Mapping[str, SystemRecords]


class Snapshot(RecordsMap, CosseratRodRecordsMixin, SphereRecordsMixin):
    """Data access for a single snapshot of an Elastica++ simulation.

    Args:
        node (node): Node in which to lookup the temporal information.
        transforms (callable, optional): A function/transform that takes in an array
            data-structure and returns a transformed version.
            E.g, ``transforms.ToArray``
    """

    def __init__(self, node: Node, transforms: Optional[FuncType] = None) -> None:
        """Initializer."""
        self.node = node
        self.transforms = transforms
        # mypy complains about HasRecordTraits not being met.
        self.return_lut: Dict[str, Type[SystemRecords]]
        self.return_lut = {
            name(x): x for x in SystemRecords.__subclasses__()  # type: ignore[arg-type]
        }

    def __getitem__(self, k: str) -> SystemRecords:  # noqa
        return_type = self.return_lut[k]
        return return_type(self.node[k], self.transforms)

    def __iter__(self) -> Iterator[str]:  # noqa
        return iter(self.node)

    def __len__(self) -> int:  # noqa
        return len(self.node)

    def systems(self) -> ChainMap[RecordsAdapterKey, RecordLeafs]:
        """Access all system records.

        Returns:
            Records across all systems.
        """
        # map() does not play well with inference.
        return ChainMap(*map(RecordsAdapter, self.values()))  # type: ignore[arg-type]
