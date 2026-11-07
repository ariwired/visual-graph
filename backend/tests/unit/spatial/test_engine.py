import pytest

from visual_graph.spatial import (
    BoundingBox,
    Relationship,
    RelationType,
    SpatialObject,
    compute_relationships,
)


def scene() -> list[SpatialObject]:
    return [
        SpatialObject("person", BoundingBox(0, 0, 100, 200)),
        SpatialObject("dog", BoundingBox(120, 150, 200, 200)),
        SpatialObject("bike", BoundingBox(500, 0, 700, 200)),
    ]


def test_no_self_relations() -> None:
    for rel in compute_relationships(scene()):
        assert rel.source_id != rel.target_id


def test_single_object_has_no_relationships() -> None:
    assert compute_relationships(scene()[:1]) == []
    assert compute_relationships([]) == []


def test_expected_relationships() -> None:
    rels = set(compute_relationships(scene()))
    assert Relationship("person", RelationType.LEFT_OF, "bike") in rels
    assert Relationship("bike", RelationType.RIGHT_OF, "person") in rels
    assert Relationship("person", RelationType.NEAR, "dog") in rels
    assert Relationship("dog", RelationType.BELOW, "person") in rels


def test_symmetric_relations_emitted_once_per_pair() -> None:
    objs = [
        SpatialObject("a", BoundingBox(0, 0, 100, 100)),
        SpatialObject("b", BoundingBox(50, 50, 150, 150)),
    ]
    rels = compute_relationships(objs)
    assert Relationship("a", RelationType.OVERLAPS, "b") in rels
    assert Relationship("b", RelationType.OVERLAPS, "a") not in rels
    assert sum(r.type is RelationType.NEAR for r in rels) == 1


def test_deterministic() -> None:
    assert compute_relationships(scene()) == compute_relationships(scene())


def test_duplicate_ids_are_rejected() -> None:
    box = BoundingBox(0, 0, 1, 1)
    with pytest.raises(ValueError, match="unique"):
        compute_relationships([SpatialObject("x", box), SpatialObject("x", box)])
