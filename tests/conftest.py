"""
Pytest Fixtures for Multimodal EHR CDSS Test Suite
"""

import pytest
from fastapi.testclient import TestClient

from src.api.main import app


@pytest.fixture
def client():
    """
    TestClient fixture for FastAPI application testing.
    """
    with TestClient(app) as test_client:
        yield test_client
