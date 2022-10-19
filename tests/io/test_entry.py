"""Tests the entry points into IO module."""
from pathlib import Path

import pytest

from elastica_pipelines.io.entry import series
from tests.io.test_protocols import skip_if_env_has


THIS_DIR = Path(__file__).parent


def iterate_series_metadata(metadata_file):
    """Iterate over a series with metadata."""
    for t, snapshot in series(metadata=metadata_file).items():
        assert t.iterate > 0
        for rod_id, rod in snapshot.cosserat_rods().items():
            assert rod_id >= 0
            for attribute, data in rod.items():
                assert attribute
                assert data.shape


@pytest.mark.e2e
class TestSeriesEntry:
    """Test the series entry point."""

    def test_series_throw_both_options(self):
        """Test both series and metadata option."""
        with pytest.raises(RuntimeError, match="Both"):
            file_pattern = "elastica_%T.h5"
            metadata_file = THIS_DIR / "some_random_path" / "elastica_metadata.h5"
            series(file_pattern=file_pattern, metadata=metadata_file)

    def test_series_throw_no_options(self):
        """Test neither series and metadata option."""
        with pytest.raises(RuntimeError, match="Either"):
            series()

    def test_metadata_throw_incorrect_file(self):
        """Test incorrect file."""
        metadata_file = THIS_DIR / "some_random_path" / "elastica_metadata.h5"
        with pytest.raises(FileNotFoundError):
            iterate_series_metadata(metadata_file)

    def test_metadata_throw_not_file(self):
        """Test path inputs."""
        metadata_file = THIS_DIR / "data"
        with pytest.raises(IOError):
            iterate_series_metadata(metadata_file)

    def test_metadata_throw_unsupported_backend(self):
        """Test unsupported backend."""
        metadata_file = THIS_DIR / "data" / "elastica_metadata.yml"
        metadata_file.touch(exist_ok=True)
        with pytest.raises(RuntimeError, match="Unsupported"):
            iterate_series_metadata(metadata_file)
        metadata_file.unlink()

    def test_series_pattern(self):
        """Test series with pattern file."""
        with pytest.raises(NotImplementedError):
            file_pattern = "elastica_%T.h5"
            series(file_pattern=file_pattern)

    # Needs Accessor which needs runtime checkable
    @skip_if_env_has("typeguard")
    def test_series_metadata(self):
        """Tests series with metadata file."""
        metadata_file = THIS_DIR / "data" / "elastica_metadata.h5"
        iterate_series_metadata(metadata_file)
