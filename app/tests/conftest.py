"""Shared pytest fixtures for application testing."""

import os
import sys
import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from app import app as flask_app


@pytest.fixture
def client():
    """Shared Flask test client fixture for all test modules."""
    flask_app.testing = True
    with flask_app.test_client() as test_client:
        yield test_client
