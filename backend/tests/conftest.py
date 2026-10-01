import pytest
from fastapi.testclient import TestClient

from visual_graph.main import create_app


@pytest.fixture
def client() -> TestClient:
    return TestClient(create_app())
