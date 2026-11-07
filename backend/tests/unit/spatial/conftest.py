import pytest

from visual_graph.spatial import BoundingBox, SpatialConfig


@pytest.fixture
def box() -> BoundingBox:
    """Reference box: 100x100 at the origin."""
    return BoundingBox(0, 0, 100, 100)


@pytest.fixture
def config() -> SpatialConfig:
    return SpatialConfig()
