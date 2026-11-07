"""Compute spatial relationships for all objects detected in one image."""

from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass

from visual_graph.spatial.bbox import BoundingBox
from visual_graph.spatial.relations import (
    DEFAULT_CONFIG,
    SYMMETRIC_RELATIONS,
    RelationType,
    SpatialConfig,
    holds,
)


@dataclass(frozen=True, slots=True)
class SpatialObject:
    """An identified object with a bounding box (detector-agnostic)."""

    id: str
    bbox: BoundingBox


@dataclass(frozen=True, slots=True)
class Relationship:
    source_id: str
    type: RelationType
    target_id: str


def compute_relationships(
    objects: Sequence[SpatialObject],
    config: SpatialConfig = DEFAULT_CONFIG,
) -> list[Relationship]:
    """Return every spatial relationship between distinct objects.

    * An object is never related to itself.
    * Directional relations are emitted for each ordered pair.
    * Symmetric relations (``NEAR``, ``OVERLAPS``) are emitted once per unordered
      pair, from the object that appears first in ``objects``.
    * The output order depends only on the input order, so equal inputs always
      produce equal outputs.

    Raises:
        ValueError: if two objects share the same id.
    """
    ids = [obj.id for obj in objects]
    if len(set(ids)) != len(ids):
        raise ValueError("object ids must be unique")

    result: list[Relationship] = []
    for i, first in enumerate(objects):
        for j, second in enumerate(objects):
            if i == j:
                continue
            for relation in RelationType:
                if relation in SYMMETRIC_RELATIONS and j < i:
                    continue
                if holds(relation, first.bbox, second.bbox, config):
                    result.append(Relationship(first.id, relation, second.id))
    return result
