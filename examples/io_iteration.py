"""Lazy loading of Elastica++ simulation data."""
import os
from pathlib import Path

from elastica_pipelines import io


# Metadata file written by Elastica++.
metadata_fn = Path("..") / "tests" / "io" / "data" / "elastica_metadata.h5"

# Disable libhdf5 file locking since we only read files
# This needs to be done before any import of h5py, so before reading a series
os.environ["HDF5_USE_FILE_LOCKING"] = "FALSE"

# Create read only access to data written by Elastica++.
series = io.series(metadata=metadata_fn)

# use series like a python Mapping.
for t, snapshot in series.iterations():
    print(f"Iteration: {t.iterate} at time {t.time}")

    # Snapshot is a mapping contain system types such as CosseratRods & Spheres.
    # Here we access only cosserat rods only.
    for (
        rod_id,
        rod,
    ) in snapshot.cosserat_rods().items():  # snapshot['CosseratRod'] also works!
        if rod_id == 0:
            print(f"  Rod {rod_id!r} attributes:")
            # Even rod is a Mapping, so we get its keys...
            print(f"  {list(rod.keys())}")
        # and then access it values.
        print(f"  Rod {rod_id!r} position:", rod["Position"])

    # To access all rod types (CosseratRod, CosseratRodWithoutDamping etc.),
    # use the rods() method
    for (
        rod_id,
        rod,
    ) in snapshot.rods().items():
        # and then access it values.
        print(f"  Rod {rod_id!r} position:", rod["Position"])
