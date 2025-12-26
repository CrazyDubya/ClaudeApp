"""
Pytest configuration and fixtures for curriculum validation tests.

These tests validate that curriculum examples work correctly
against the current version of the Claude SDK.
"""

import os
import pytest


@pytest.fixture(scope="session")
def validation_mode():
    """Enable validation mode for tests."""
    os.environ["FORGE_VALIDATION_MODE"] = "1"
    yield True
    del os.environ["FORGE_VALIDATION_MODE"]


@pytest.fixture(scope="session")
def sdk_available():
    """Check if the Anthropic SDK is available."""
    try:
        import anthropic
        return True
    except ImportError:
        return False


@pytest.fixture(scope="session")
def api_key_available():
    """Check if an API key is configured."""
    return bool(os.environ.get("ANTHROPIC_API_KEY"))


@pytest.fixture
def skip_without_api(api_key_available):
    """Skip test if no API key is available."""
    if not api_key_available:
        pytest.skip("ANTHROPIC_API_KEY not set")


@pytest.fixture
def client(skip_without_api):
    """Create an Anthropic client for testing."""
    from anthropic import Anthropic
    return Anthropic()
