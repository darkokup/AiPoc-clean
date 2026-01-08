"""Pytest configuration for additional test options."""
import pytest


def pytest_addoption(parser):
    """Add custom pytest command line options."""
    parser.addoption(
        "--run-llm",
        action="store_true",
        default=False,
        help="Run tests that require LLM API calls (expensive)"
    )
    parser.addoption(
        "--run-slow",
        action="store_true",
        default=False,
        help="Run slow tests"
    )


def pytest_configure(config):
    """Register custom markers."""
    config.addinivalue_line(
        "markers", "llm: marks tests that require LLM API calls (expensive)"
    )
    config.addinivalue_line(
        "markers", "slow: marks tests as slow (deselect with '-m \"not slow\"')"
    )


def pytest_collection_modifyitems(config, items):
    """Skip tests based on command line options."""
    if not config.getoption("--run-llm"):
        skip_llm = pytest.mark.skip(reason="need --run-llm option to run")
        for item in items:
            if "llm" in item.keywords:
                item.add_marker(skip_llm)
    
    if not config.getoption("--run-slow"):
        skip_slow = pytest.mark.skip(reason="need --run-slow option to run")
        for item in items:
            if "slow" in item.keywords:
                item.add_marker(skip_slow)
