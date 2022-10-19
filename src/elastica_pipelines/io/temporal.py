"""Temporal IO types."""
from __future__ import annotations

from collections.abc import Iterator
from dataclasses import dataclass
from typing import Any
from typing import ChainMap
from typing import Dict
from typing import ItemsView
from typing import Mapping
from typing import Optional
from typing import Type
from typing import Union

from typing_extensions import Protocol
from typing_extensions import TypeAlias

from elastica_pipelines.io.backends import accessor
from elastica_pipelines.io.core import RecordsIndexedOp
from elastica_pipelines.io.core import RecordsSliceOp
from elastica_pipelines.io.core import SystemRecords
from elastica_pipelines.io.protocols import ElasticaConvention
from elastica_pipelines.io.protocols import SystemIndices
from elastica_pipelines.io.protocols import name
from elastica_pipelines.io.specialize import CosseratRodRecords
from elastica_pipelines.io.specialize import CosseratRodRecordTraits
from elastica_pipelines.io.specialize import CosseratRodWithoutDampingRecords
from elastica_pipelines.io.specialize import CosseratRodWithoutDampingRecordTraits
from elastica_pipelines.io.specialize import SphereRecords
from elastica_pipelines.io.specialize import SphereRecordTraits
from elastica_pipelines.io.typing import FuncType
from elastica_pipelines.io.typing import Node
from elastica_pipelines.io.typing import RecordLeafs


"""Implementation of snapshot-specific functionality."""


@dataclass(eq=True, frozen=True)
class RecordsAdapterKey:
    """Key containing both the type and id of the system, for iteration.

    Args:
        sys_type: Type of the system.
        sys_id: Unique ID of the system.

    """

    sys_type: str
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


class CosseratRodWithoutDampingRecordsMixin:
    """Mixin for cosserat_rods_without_damping() access."""

    def cosserat_rods_without_damping(
        self: HasGetItem,
    ) -> CosseratRodWithoutDampingRecords:
        """Access cosserat rod without damping records.

        Returns:
            CosseratRodWithoutDamping records.
        """
        return self.__getitem__(CosseratRodWithoutDampingRecordTraits.name())


class SphereRecordsMixin:
    """Mixin for spheres() access."""

    def spheres(self: HasGetItem) -> SphereRecords:
        """Access sphere records.

        Returns:
            Sphere records.
        """
        return self.__getitem__(SphereRecordTraits.name())


class HasItems(HasGetItem, Protocol):
    """Has items protocol."""

    def items(self) -> Any:  # noqa
        ...  # pragma: no cover


class RodRecordsMixin(CosseratRodRecordsMixin, CosseratRodWithoutDampingRecordsMixin):
    """Mixin for rods() access."""

    def rods(self: HasItems) -> ChainMap[RecordsAdapterKey, RecordLeafs]:
        """Access all rod records.

        Returns:
            Records across all rods.

        Example:
            >>> from elastica_pipelines.io import series
            >>> from elastica_pipelines.io.temporal import Snapshot
            >>>
            >>> # ``series`` returns a ``Series`` object
            >>> metadata_filename = "tests/io/data/elastica_metadata.h5"
            >>> s = series(metadata=metadata_filename)
            >>> snap : Snapshot = s[50] # lookup the data at iteration 50

            >>> # Iterate over all rods regardless of the type
            >>> for sys_id, system in snap.rods().items():
            >>>     print(sys_id, system)
        """
        # map() does not play well with type inference.
        return ChainMap(
            *map(  # type: ignore[arg-type]
                RecordsAdapter,
                map(
                    lambda y: y[1],  # Extract only values
                    filter(  # Filter based on keys
                        lambda x: CosseratRodRecordTraits.name() in x[0], self.items()
                    ),
                ),
            )
        )


RecordsMap: TypeAlias = Mapping[str, SystemRecords]


class Snapshot(
    RecordsMap,
    RodRecordsMixin,
    SphereRecordsMixin,
):
    """Data access for a single snapshot of an Elastica++ simulation.

    Args:
        node : Node in which to lookup the information at one time iterate.
        transforms (Callable, Optional): A function/transform that takes in an array
            data-structure and returns a transformed version.
            E.g, ``transforms.ToArray``

    Example:
        >>> from elastica_pipelines.io import series
        >>> from elastica_pipelines.io.temporal import Snapshot
        >>>
        >>> # ``series`` returns a ``Series`` object
        >>> metadata_filename = "tests/io/data/elastica_metadata.h5"
        >>> s = series(metadata=metadata_filename)

        >>> snap : Snapshot = s[50] # lookup the data at iteration 50

        >>> cosserat_rod_records = snap["CosseratRod"] # dict-like interface
        >>> for system_type in snap.keys(): # obtain all system types
        >>>     print(system_type, snap[system_type])
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

        Example:
            >>> from elastica_pipelines.io import series
            >>> from elastica_pipelines.io.temporal import Snapshot
            >>>
            >>> # ``series`` returns a ``Series`` object
            >>> metadata_filename = "tests/io/data/elastica_metadata.h5"
            >>> s = series(metadata=metadata_filename)
            >>> snap : Snapshot = s[50] # lookup the data at iteration 50

            >>> # Iterate over all systems regardless of the type
            >>> for sys_id, system in snap.systems().items():
            >>>     print(sys_id, system)
        """
        # map() does not play well with inference.
        return ChainMap(*map(RecordsAdapter, self.values()))  # type: ignore[arg-type]


"""Implementation of series functionality."""


@dataclass(frozen=True, eq=True)
class SeriesKey:
    """Key for a temporal series.

    Args:
        iterate: Unique iteration value
        time: Time for current iteration
        dt: Timestep for current iteration

    """

    iterate: int
    time: float
    dt: float


class SeriesIterator:
    """Iterator for adapted records.

    Args:
        node (Node): Node with series information.
    """

    def __init__(self, node: Node) -> None:
        """Initializer."""
        self.node = node
        self.it = iter(self.node)

    def __iter__(self) -> SeriesIterator:  # noqa
        return self

    def __next__(self) -> SeriesKey:  # noqa
        n = int(next(self.it))
        record_node = self.node[ElasticaConvention.as_record_key(n)]
        backend = accessor(record_node)
        return SeriesKey(
            n, backend.access_time(record_node), backend.access_dt(record_node)
        )


SeriesKeys: TypeAlias = Union[int, SeriesKey]


class Series(Mapping[SeriesKeys, Snapshot]):
    """Temporally evolving data-series.

    Has the same interface as a dictionary, and hence lookup, items() work.

    Args:
        node : Node with series information.
        transforms (Callable, Optional): A function/transform that takes in an array
            data-structure and returns a transformed version.
            E.g, ``transforms.ToArray``

    Example:
        >>> from elastica_pipelines.io import series
        >>> from elastica_pipelines.io.temporal import Series
        >>>
        >>> # ``series`` returns a ``Series`` object
        >>> metadata_filename = "tests/io/data/elastica_metadata.h5"
        >>> s : Series = series(metadata=metadata_filename)

        >>> s[50] # lookup the data at iteration 50, iterates may not be continuous!

        >>> for t in s.keys(): # obtain all iteration values
        >>>     print(t.iterate, t.time, t.dt)
        >>>     print(s[t])
    """

    def __init__(self, node: Node, transforms: Optional[FuncType] = None) -> None:
        """Initializer."""
        self.node = node
        self.transforms = transforms

    def __getitem__(self, k: SeriesKeys) -> Snapshot:  # noqa
        # convention
        if isinstance(k, int):
            return Snapshot(
                ElasticaConvention.access(
                    self.node[ElasticaConvention.as_record_key(k)]
                ),
                self.transforms,
            )
        else:
            return self.__getitem__(k.iterate)

    def __iter__(self) -> SeriesIterator:  # noqa
        return SeriesIterator(self.node)

    def __len__(self) -> int:  # noqa
        return len(self.node)

    def temporal_select(self, indices: SystemIndices) -> SeriesSelection:
        """Obtain temporal evolution for a select subset of systems.

        Args:
            indices(SystemIndices): indices (with Traits) for system selection.

        Returns:
            ``SeriesSelection`` with the same interface.

        Example:
            >>> from elastica_pipelines.io import series
            >>> from elastica_pipelines.io.temporal import Series
            >>> from elastica_pipelines.io import CosseratRodRecordIndex
            >>>
            >>> metadata_filename = "tests/io/data/elastica_metadata.h5"
            >>> s : Series = series(metadata=metadata_filename)
            >>>
            >>> # Select Cosserat rod with ID 1
            >>> subset = s.temporal_select(CosseratRodRecordIndex(1))
            >>> # Select Cosserat rod with list of indices
            >>> subset = s.temporal_select(CosseratRodRecordIndex([1, 3]))
            >>> # Select Cosserat rod range with indices
            >>> subset = s.temporal_select(CosseratRodRecordIndex(slice(1,5,2)))
            >>>
            >>> # Subset has same interface as Series, see SeriesSelection
            >>> for t in subset.keys(): # obtain all iteration values
            >>>     print(t.iterate, t.time, t.dt)
            >>>     print(subset[t])
        """
        return SeriesSelection(self, indices)

    def iterations(self) -> ItemsView[SeriesKeys, Snapshot]:
        """Obtain temporal iterations.

        Returns:
            Temporal iteration
        """
        return self.items()


class SeriesSelection(Mapping[SeriesKeys, RecordLeafs]):
    """Temporally evolving data-series restricted to a subset of systems.

    Args:
        parent (Series): Series from which the selection is made.
        indices (SystemIndices): Selection of index subsets

    Example:
        >>> from elastica_pipelines.io import series
        >>> from elastica_pipelines.io.temporal import Series, SeriesSelection
        >>> from elastica_pipelines.io import CosseratRodRecordIndex as RodIndex
        >>>
        >>> metadata_filename = "tests/io/data/elastica_metadata.h5"
        >>> s : Series = series(metadata=metadata_filename)
        >>>
        >>> # Select Cosserat rod with list of indices
        >>> subset : SeriesSelection = s.temporal_select(RodIndex([1, 4, 9]))
        >>>
        >>> # Subset has same interface as Series
        >>> subset[50] # lookup the data at iteration 50
        >>>
        >>> for t in subset.keys(): # obtain all iteration values for subsets
        >>>     print(t.iterate, t.time, t.dt)
        >>>     print(subset[t])
    """

    def __init__(self, parent: Series, indices: SystemIndices):  # noqa
        """Initializer."""
        self.parent = parent
        self.indices = indices

    def __getitem__(self, k: SeriesKeys) -> RecordLeafs:  # noqa
        # [Time][System][Index]
        return self.parent[k][name(self.indices)][self.indices.indices]

    def __iter__(self) -> SeriesIterator:  # noqa
        return iter(self.parent)

    def __len__(self) -> int:  # noqa
        return len(self.parent)

    def temporal_select(self, indices: SystemIndices) -> SeriesSelection:
        """Obtain temporal evolution for a select subset of systems.

        Args:
            indices(SystemIndices): indices (with Traits) for system selection.

        Returns:
            ``SeriesSelection`` with the same interface.

        Raises:
            TypeError: If index is out of bounds.

        Example:
            >>> from elastica_pipelines.io import series
            >>> from elastica_pipelines.io.temporal import Series, SeriesSelection
            >>> from elastica_pipelines.io import CosseratRodRecordIndex as RodIndex
            >>>
            >>> metadata_filename = "tests/io/data/elastica_metadata.h5"
            >>> ser : Series = series(metadata=metadata_filename)
            >>>
            >>> s : SeriesSelection = ser.temporal_select(RodIndex([1, 2, 3]))
            >>>
            >>> # Select Cosserat rod with list of indices
            >>> subset : SeriesSelection = s.temporal_select(RodIndex([1, 2]))
            >>>
            >>> # Subset has same interface as Series
            >>> subset[50] # lookup the data at iteration 50
            >>>
            >>> for t in subset.keys(): # obtain all iteration values for subsets
            >>>     print(t.iterate, t.time, t.dt)
            >>>     print(subset[t])

        .. note::
                The subset of indices requested must be contained within the
                bounds alredy selected, else an error is thrown.
        """
        t = type(indices)
        if not isinstance(self.indices, t):
            raise TypeError(
                f"Requested type {t.__class__.__name__} of system indices does "
                f"not match with the selection{type(self.indices).__class__.__name__}"
            )

        snap = next(iter(self.parent.values()))
        n_records = len(snap[name(self.indices)])

        i = self.indices.indices

        op_indices: Union[RecordsIndexedOp, RecordsSliceOp] = (
            RecordsSliceOp(slice(*i.indices(n_records)))
            if isinstance(i, slice)
            else RecordsIndexedOp([i])
            if isinstance(i, int)
            else RecordsIndexedOp(i)
        )
        return self.parent.temporal_select(
            t(
                op_indices.get_index_into_slice(
                    indices.indices, op_indices.get_length_of_slice(n_records)
                )
            )
        )

    def iterations(self) -> ItemsView[SeriesKeys, RecordLeafs]:
        """Obtain temporal iterations.

        Returns:
            Temporal iteration
        """
        return self.items()
