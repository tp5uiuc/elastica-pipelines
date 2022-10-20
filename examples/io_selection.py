"""Selecting subsets of Elastica++ data and lazy loading."""
import os
from pathlib import Path

from elastica_pipelines import io


metadata_fn = Path("..") / "tests" / "io" / "data" / "elastica_metadata.h5"

# Disable libhdf5 file locking since we only read files
# This needs to be done before any import of h5py, so before reading a series
os.environ["HDF5_USE_FILE_LOCKING"] = "FALSE"

series = io.series(metadata=metadata_fn)

# Suppose we are only interested in the evolution of rods with rod_id 1, 3.
# We explicitly request access using `temporal_select`

# CosseratRodRecordIndex is necessary to indicate we are interested in rods
# and not, say spheres
subset = series.temporal_select(io.CosseratRodRecordIndex([1, 3]))
# You can also pass in a single index like so...
subset = series.temporal_select(io.CosseratRodRecordIndex(1))
# Or even slices.
subset = series.temporal_select(io.CosseratRodRecordIndex(slice(1, 5, 2)))


# To select another system type, such as a sphere use
# subset = series.temporal_select(io.SphereRecordIndex([1, 3]))

# Use subset with the exact same interface as a io series.
for t, snapshot in subset.iterations():
    print(f"Iteration: {t.iterate} at time {t.time}")

    # Use the same map interface!
    for (rod_id, rod) in snapshot.items():
        print(f"  Rod '{rod_id}' elements:")
        print("  Rod elements:", rod["NElement"])
