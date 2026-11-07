import pytest

from visual_graph.spatial import BoundingBox, SpatialConfig
from visual_graph.spatial.relations import (
    above,
    below,
    gap_distance,
    intersection_area,
    left_of,
    near,
    overlaps,
    right_of,
)

REF = BoundingBox(0, 0, 100, 100)  # center (50, 50)


# --- horizontal -----------------------------------------------------------
def test_left_and_right_of() -> None:
    right = BoundingBox(200, 0, 300, 100)
    assert left_of(REF, right) and right_of(right, REF)
    assert not left_of(right, REF) and not right_of(REF, right)


def test_equal_centers_are_neither_left_nor_right() -> None:
    other = BoundingBox(25, 0, 75, 100)  # same center_x
    assert not left_of(REF, other) and not right_of(REF, other)


def test_left_of_with_partial_overlap_uses_centers() -> None:
    other = BoundingBox(50, 0, 150, 100)
    assert left_of(REF, other)


def test_directional_margin_boundary() -> None:
    cfg = SpatialConfig(directional_margin=0.5)
    exactly = BoundingBox(50, 0, 150, 100)  # center offset 50 == 0.5 * 100
    beyond = BoundingBox(51, 0, 151, 100)
    assert not left_of(REF, exactly, cfg)
    assert left_of(REF, beyond, cfg)


# --- vertical (y grows downward) --------------------------------------------
def test_above_and_below() -> None:
    lower = BoundingBox(0, 200, 100, 300)
    assert above(REF, lower) and below(lower, REF)
    assert not above(lower, REF) and not below(REF, lower)


def test_equal_centers_are_neither_above_nor_below() -> None:
    other = BoundingBox(0, 25, 100, 75)
    assert not above(REF, other) and not below(REF, other)


def test_diagonal_pair_satisfies_both_axes() -> None:
    other = BoundingBox(200, 200, 300, 300)
    assert left_of(REF, other) and above(REF, other)


# --- NEAR -------------------------------------------------------------------
def test_near_exactly_at_threshold_is_inclusive() -> None:
    # near_ratio 0.5 * scale 100 = 50
    at = BoundingBox(150, 0, 250, 100)
    assert gap_distance(REF, at) == 50
    assert near(REF, at)


def test_near_slightly_outside_threshold() -> None:
    outside = BoundingBox(150.001, 0, 250.001, 100)
    assert not near(REF, outside)


def test_near_uses_euclidean_gap_on_diagonals() -> None:
    cfg = SpatialConfig(near_ratio=0.5)
    diagonal = BoundingBox(130, 140, 230, 240)  # dx=30, dy=40 -> gap 50
    assert gap_distance(REF, diagonal) == pytest.approx(50)
    assert near(REF, diagonal, cfg)
    assert not near(REF, BoundingBox(130, 141, 230, 241), cfg)


def test_near_threshold_is_configurable() -> None:
    far = BoundingBox(300, 0, 400, 100)  # gap 200
    assert not near(REF, far)
    assert near(REF, far, SpatialConfig(near_ratio=2.0))


def test_touching_and_overlapping_boxes_are_near() -> None:
    assert near(REF, BoundingBox(100, 0, 200, 100))
    assert near(REF, BoundingBox(50, 50, 150, 150))


def test_near_is_symmetric() -> None:
    other = BoundingBox(150, 0, 250, 100)
    assert near(REF, other) == near(other, REF)


# --- OVERLAPS -----------------------------------------------------------------
def test_partial_overlap() -> None:
    other = BoundingBox(50, 50, 150, 150)
    assert intersection_area(REF, other) == 2500
    assert overlaps(REF, other) and overlaps(other, REF)


def test_complete_containment_overlaps() -> None:
    inner = BoundingBox(25, 25, 75, 75)
    assert overlaps(REF, inner) and overlaps(inner, REF)


def test_identical_boxes_overlap() -> None:
    assert overlaps(REF, BoundingBox(0, 0, 100, 100))


@pytest.mark.parametrize(
    "other",
    [
        BoundingBox(100, 0, 200, 100),  # shared vertical edge
        BoundingBox(0, 100, 100, 200),  # shared horizontal edge
        BoundingBox(100, 100, 200, 200),  # shared corner
    ],
)
def test_touching_boundaries_do_not_overlap(other: BoundingBox) -> None:
    assert intersection_area(REF, other) == 0
    assert not overlaps(REF, other)


def test_disjoint_boxes_do_not_overlap() -> None:
    assert not overlaps(REF, BoundingBox(200, 200, 300, 300))


def test_min_overlap_ratio_boundary() -> None:
    cfg = SpatialConfig(min_overlap_ratio=0.25)
    exactly = BoundingBox(50, 50, 150, 150)  # 2500 / 10000 == 0.25
    more = BoundingBox(49, 49, 149, 149)
    assert not overlaps(REF, exactly, cfg)
    assert overlaps(REF, more, cfg)


# --- config validation -------------------------------------------------------------
@pytest.mark.parametrize(
    "kwargs",
    [
        {"directional_margin": -0.1},
        {"near_ratio": -1},
        {"min_overlap_ratio": -0.1},
        {"min_overlap_ratio": 1.0},
    ],
)
def test_invalid_config_is_rejected(kwargs: dict[str, float]) -> None:
    with pytest.raises(ValueError):
        SpatialConfig(**kwargs)
