"""Selecting subsets of Elastica++ data and lazy loading."""
from pathlib import Path

from elastica_pipelines import io


metadata_fn = Path("..") / "tests" / "io" / "data" / "elastica_metadata.h5"
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
