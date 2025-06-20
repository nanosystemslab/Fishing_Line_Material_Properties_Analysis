"""Pytest configuration and fixtures."""

import matplotlib
import matplotlib.pyplot as plt
import pytest


matplotlib.use("Agg")  # Use non-interactive backend for all tests


@pytest.fixture(autouse=True)
def setup_matplotlib():
    """Setup matplotlib for testing."""
    # Set non-interactive backend
    matplotlib.use("Agg")
    plt.ioff()  # Turn off interactive mode

    yield

    # Clean up all figures after each test
    plt.close("all")
    plt.clf()  # Clear current figure
    plt.cla()  # Clear current axes


@pytest.fixture(autouse=True)
def no_network():
    """Disable network access during tests."""
    import socket

    def guard(*args, **kwargs):
        raise Exception("Network access not allowed during tests")

    socket.socket = guard
