"""Adding transforms to Elastica++ series."""
import os
from pathlib import Path

from elastica_pipelines import io


metadata_fn = Path("..") / "tests" / "io" / "data" / "elastica_metadata.h5"

# Disable libhdf5 file locking since we only read files
# This needs to be done before any import of h5py, so before reading a series
os.environ["HDF5_USE_FILE_LOCKING"] = "FALSE"

# Add transformations to the data using the transforms module.
# ToArray() converts the data to a numpy array
series = io.series(metadata=metadata_fn, transforms=io.transforms.ToArray())

# You can also write your own transformations and compose them using Compose
# We convert the data to numpy and then transpose it here.
series = io.series(
    metadata=metadata_fn,
    transforms=io.transforms.Compose([io.transforms.ToArray(), lambda x: x.T]),
)

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
