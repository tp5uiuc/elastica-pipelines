"""Test configuration."""


def pytest_configure(config):
    """Adds custom test configuration."""
    config.addinivalue_line("markers", "e2e: mark as end-to-end test.")
