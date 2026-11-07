"""Deterministic geometric predicates between two bounding boxes.

Every predicate is a pure function of its inputs: it does not depend on Neo4j,
on a detector, or on any global state. See ``docs/spatial-relationships.md``
for the mathematical definition of each rule.
"""

from __future__ import annotations

import math
from dataclasses import dataclass
from enum import StrEnum

from visual_graph.spatial.bbox import BoundingBox


class RelationType(StrEnum):
    LEFT_OF = "LEFT_OF"
    RIGHT_OF = "RIGHT_OF"
    ABOVE = "ABOVE"
    BELOW = "BELOW"
    NEAR = "NEAR"
    OVERLAPS = "OVERLAPS"


#: Relations that hold in both directions; stored once per unordered pair.
SYMMETRIC_RELATIONS = frozenset({RelationType.NEAR, RelationType.OVERLAPS})


@dataclass(frozen=True, slots=True)
class SpatialConfig:
    """Explicit, configurable thresholds for the spatial rules.

    Attributes:
        directional_margin: Fraction of the larger box dimension (width for
            LEFT_OF/RIGHT_OF, height for ABOVE/BELOW) by which the centers must
            differ. ``0.0`` means any strict center difference counts.
        near_ratio: NEAR holds when the gap between the boxes is at most
            ``near_ratio * max(width, height)`` of the larger box.
        min_overlap_ratio: OVERLAPS requires the intersection area to be
            strictly greater than ``min_overlap_ratio * min(area_a, area_b)``.
            ``0.0`` means any positive-area intersection counts.
    """

    directional_margin: float = 0.0
    near_ratio: float = 0.5
    min_overlap_ratio: float = 0.0

    def __post_init__(self) -> None:
        if self.directional_margin < 0:
            raise ValueError("directional_margin must be >= 0")
        if self.near_ratio < 0:
            raise ValueError("near_ratio must be >= 0")
        if not 0 <= self.min_overlap_ratio < 1:
            raise ValueError("min_overlap_ratio must be in [0, 1)")


DEFAULT_CONFIG = SpatialConfig()


def left_of(a: BoundingBox, b: BoundingBox, config: SpatialConfig = DEFAULT_CONFIG) -> bool:
    """``a`` is left of ``b`` when ``b.cx - a.cx > margin * max(a.w, b.w)``."""
    return b.center_x - a.center_x > config.directional_margin * max(a.width, b.width)


def right_of(a: BoundingBox, b: BoundingBox, config: SpatialConfig = DEFAULT_CONFIG) -> bool:
    """``a`` is right of ``b`` exactly when ``b`` is left of ``a``."""
    return left_of(b, a, config)


def above(a: BoundingBox, b: BoundingBox, config: SpatialConfig = DEFAULT_CONFIG) -> bool:
    """``a`` is above ``b`` when ``b.cy - a.cy > margin * max(a.h, b.h)`` (y grows downward)."""
    return b.center_y - a.center_y > config.directional_margin * max(a.height, b.height)


def below(a: BoundingBox, b: BoundingBox, config: SpatialConfig = DEFAULT_CONFIG) -> bool:
    """``a`` is below ``b`` exactly when ``b`` is above ``a``."""
    return above(b, a, config)


def intersection_area(a: BoundingBox, b: BoundingBox) -> float:
    """Area of the intersection of two boxes (``0.0`` if disjoint or touching)."""
    dx = min(a.x_max, b.x_max) - max(a.x_min, b.x_min)
    dy = min(a.y_max, b.y_max) - max(a.y_min, b.y_min)
    if dx <= 0 or dy <= 0:
        return 0.0
    return dx * dy


def gap_distance(a: BoundingBox, b: BoundingBox) -> float:
    """Euclidean distance between the closest edges of two boxes (``0`` if they touch/overlap)."""
    dx = max(a.x_min - b.x_max, b.x_min - a.x_max, 0.0)
    dy = max(a.y_min - b.y_max, b.y_min - a.y_max, 0.0)
    return math.hypot(dx, dy)


def overlaps(a: BoundingBox, b: BoundingBox, config: SpatialConfig = DEFAULT_CONFIG) -> bool:
    """Boxes overlap when ``area(a ∩ b) > min_overlap_ratio * min(area a, area b)`` and > 0.

    Boxes that only touch along an edge or corner do not overlap.
    """
    inter = intersection_area(a, b)
    return inter > 0 and inter > config.min_overlap_ratio * min(a.area, b.area)


def near(a: BoundingBox, b: BoundingBox, config: SpatialConfig = DEFAULT_CONFIG) -> bool:
    """Boxes are near when ``gap_distance <= near_ratio * max(w, h of the larger box)``.

    The threshold is inclusive. Overlapping or touching boxes have gap ``0`` and
    are therefore near.
    """
    scale = max(a.width, a.height, b.width, b.height)
    return gap_distance(a, b) <= config.near_ratio * scale


_PREDICATES = {
    RelationType.LEFT_OF: left_of,
    RelationType.RIGHT_OF: right_of,
    RelationType.ABOVE: above,
    RelationType.BELOW: below,
    RelationType.NEAR: near,
    RelationType.OVERLAPS: overlaps,
}


def holds(
    relation: RelationType,
    a: BoundingBox,
    b: BoundingBox,
    config: SpatialConfig = DEFAULT_CONFIG,
) -> bool:
    """Evaluate ``relation`` for the ordered pair ``(a, b)``."""
    return _PREDICATES[relation](a, b, config)
