import math

import pytest

from visual_graph.spatial import BoundingBox, InvalidBoundingBoxError


def test_derived_properties() -> None:
    b = BoundingBox(10, 20, 50, 100)
    assert (b.width, b.height, b.area) == (40, 80, 3200)
    assert (b.center_x, b.center_y) == (30, 60)


@pytest.mark.parametrize(
    "coords",
    [
        (0, 0, 0, 10),  # zero width
        (0, 0, 10, 0),  # zero height
        (0, 0, 0, 0),  # zero area
        (10, 0, 0, 10),  # negative width
        (0, 10, 10, 0),  # negative height
        (math.nan, 0, 10, 10),
        (0, 0, math.inf, 10),
        (0, -math.inf, 10, 10),
        ("0", 0, 10, 10),
        (None, 0, 10, 10),
        (True, 0, 10, 10),
    ],
)
def test_invalid_boxes_are_rejected(coords: tuple[object, ...]) -> None:
    with pytest.raises(InvalidBoundingBoxError):
        BoundingBox(*coords)  # type: ignore[arg-type]


def test_invalid_box_error_is_value_error() -> None:
    assert issubclass(InvalidBoundingBoxError, ValueError)
