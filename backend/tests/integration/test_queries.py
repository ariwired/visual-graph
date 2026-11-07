from collections.abc import Iterator

import pytest
from neo4j import Driver

from visual_graph.graph.connection import create_driver
from visual_graph.graph.queries import run_query
from visual_graph.graph.seed import SAMPLE_IMAGE_ID, seed_sample_scene

pytestmark = pytest.mark.integration


@pytest.fixture(scope="module")
def driver() -> Iterator[Driver]:
    drv = create_driver()
    with drv.session() as session:
        session.run("MATCH (n) DETACH DELETE n").consume()
    seed_sample_scene(drv)
    yield drv
    with drv.session() as session:
        session.run("MATCH (n) DETACH DELETE n").consume()
    drv.close()


def test_objects_in_image(driver: Driver) -> None:
    rows = run_query(driver, "objects_in_image", image_id=SAMPLE_IMAGE_ID)
    assert rows == [
        {"object_id": "sample-bicycle-1", "class": "bicycle"},
        {"object_id": "sample-chair-1", "class": "chair"},
        {"object_id": "sample-chair-2", "class": "chair"},
        {"object_id": "sample-dog-1", "class": "dog"},
        {"object_id": "sample-person-1", "class": "person"},
    ]


def test_objects_by_class_returns_every_instance(driver: Driver) -> None:
    rows = run_query(driver, "objects_by_class", class_name="chair")
    assert [r["object_id"] for r in rows] == ["sample-chair-1", "sample-chair-2"]
    assert run_query(driver, "objects_by_class", class_name="cat") == []


def test_relationships_in_image(driver: Driver) -> None:
    rows = run_query(driver, "relationships_in_image", image_id=SAMPLE_IMAGE_ID)
    triples = {(r["source"], r["relationship"], r["target"]) for r in rows}
    assert ("sample-person-1", "NEAR", "sample-dog-1") in triples
    assert ("sample-person-1", "LEFT_OF", "sample-bicycle-1") in triples
    assert ("sample-dog-1", "BELOW", "sample-person-1") in triples
    assert len(rows) == 13  # matches the seed exactly


def test_objects_near_is_symmetric(driver: Driver) -> None:
    from_person = run_query(driver, "objects_near", object_id="sample-person-1")
    from_dog = run_query(driver, "objects_near", object_id="sample-dog-1")
    assert from_person == [{"object_id": "sample-dog-1", "class": "dog"}]
    assert from_dog == [{"object_id": "sample-person-1", "class": "person"}]


def test_images_with_two_classes(driver: Driver) -> None:
    rows = run_query(driver, "images_with_two_classes", class_a="person", class_b="dog")
    assert rows == [{"image_id": SAMPLE_IMAGE_ID}]
    assert run_query(driver, "images_with_two_classes", class_a="person", class_b="cat") == []


def test_spatial_pattern_queries(driver: Driver) -> None:
    near = run_query(driver, "images_with_near_pattern", class_a="person", class_b="dog")
    assert near == [{"image_id": SAMPLE_IMAGE_ID}]
    left = run_query(driver, "images_with_left_of_pattern", class_a="person", class_b="bicycle")
    assert left == [{"image_id": SAMPLE_IMAGE_ID}]
    reverse = run_query(driver, "images_with_left_of_pattern", class_a="bicycle", class_b="person")
    assert reverse == []


def test_graph_relationships_distinguish_what_class_cooccurrence_cannot(driver: Driver) -> None:
    """A person and a chair appear in the same image, but they are not near each other.

    Class co-occurrence matches; the NEAR pattern correctly does not.
    """
    both = run_query(driver, "images_with_two_classes", class_a="person", class_b="chair")
    near = run_query(driver, "images_with_near_pattern", class_a="person", class_b="chair")
    assert both == [{"image_id": SAMPLE_IMAGE_ID}]
    assert near == []
