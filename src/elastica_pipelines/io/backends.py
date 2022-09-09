"""IO backends."""

from enum import Enum
from typing import Any
from typing import Type

from elastica_pipelines.io.protocols import BackendAccess
from elastica_pipelines.io.typing import Node


class HDF5Access:
    """Accessors for HDF5 node per Elastica++ convention."""

    @staticmethod
    def access_time(n: Node) -> float:
        """Access time from a HDF5 node, per Elastica++ convention.

        Args:
            n (Node): HDF5 Node to access data from.

        Returns:
            time from node
        """
        return n["TimeMetadata"]["time"][()]

    @staticmethod
    def access_dt(n: Node) -> float:
        """Access dt from a HDF5 node, per Elastica++ convention.

        Args:
            n (Node): HDF5 Node to access data from.

        Returns:
            dt from HDF5 node
        """
        return n["TimeMetadata"]["dt"][()]

    @staticmethod
    def access_data(n: Node) -> Any:
        """Access data from a HDF5 node, per Elastica++ convention.

        Args:
            n (Node): Node to access data from.

        Returns:
            Data from HDF5 node
        """
        return n["data"]


class SupportedBackends(Enum):
    """Supported IO Backends."""

    HDF5 = 1


def accessor(n: Node) -> Type[BackendAccess]:
    """Get accesssor based on type of node.

    Args:
        n (Node): based on which we dispatch to the right backend.

    Returns:
        Accessor conforming to the ``BackendAccess`` protocol.
    """
    return HDF5Access
