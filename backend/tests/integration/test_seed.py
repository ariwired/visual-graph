from collections.abc import Iterator

import pytest
from neo4j import Driver

from visual_graph.graph.connection import create_driver
from visual_graph.graph.seed import SAMPLE_IMAGE_ID, seed_sample_scene

pytestmark = pytest.mark.integration


@pytest.fixture
def driver() -> Iterator[Driver]:
    drv = create_driver()
    with drv.session() as session:
        session.run("MATCH (n) DETACH DELETE n").consume()
    seed_sample_scene(drv)
    yield drv
    with drv.session() as session:
        session.run("MATCH (n) DETACH DELETE n").consume()
    drv.close()


def scalar(driver: Driver, query: str) -> int:
    with driver.session() as session:
        record = session.run(query, image_id=SAMPLE_IMAGE_ID).single()
    assert record is not None
    return int(record[0])


def test_graph_shape(driver: Driver) -> None:
    assert scalar(driver, "MATCH (:Image) RETURN count(*)") == 1
    assert scalar(driver, "MATCH (:ObjectInstance) RETURN count(*)") == 5
    assert scalar(driver, "MATCH (:Class) RETURN count(*)") == 4


def test_seed_is_idempotent(driver: Driver) -> None:
    before = scalar(driver, "MATCH (n) RETURN count(n)"), scalar(
        driver, "MATCH ()-[r]->() RETURN count(r)"
    )
    seed_sample_scene(driver)
    after = scalar(driver, "MATCH (n) RETURN count(n)"), scalar(
        driver, "MATCH ()-[r]->() RETURN count(r)"
    )
    assert before == after


def test_every_instance_has_one_class_and_image(driver: Driver) -> None:
    assert (
        scalar(
            driver,
            "MATCH (o:ObjectInstance) "
            "WHERE size([(o)-[:IS_A]->(:Class) | 1]) <> 1 "
            "OR size([(:Image)-[:CONTAINS]->(o) | 1]) <> 1 RETURN count(o)",
        )
        == 0
    )


def test_multiple_instances_of_same_class(driver: Driver) -> None:
    assert (
        scalar(
            driver,
            "MATCH (:Image {id: $image_id})-[:CONTAINS]->(o)-[:IS_A]->(:Class {name: 'chair'}) "
            "RETURN count(o)",
        )
        == 2
    )


def test_spatial_relationships_are_queryable(driver: Driver) -> None:
    assert (
        scalar(
            driver,
            "MATCH (:Class {name:'person'})<-[:IS_A]-(p)-[:NEAR]-(d)"
            "-[:IS_A]->(:Class {name:'dog'}) RETURN count(*)",
        )
        == 1
    )
    assert (
        scalar(
            driver,
            "MATCH (:Class {name:'person'})<-[:IS_A]-(p)-[:LEFT_OF]->(b)-[:IS_A]->"
            "(:Class {name:'bicycle'}) RETURN count(*)",
        )
        == 1
    )
    assert (
        scalar(
            driver,
            "MATCH (:Class {name:'dog'})<-[:IS_A]-(d)-[:BELOW]->(p)-[:IS_A]->"
            "(:Class {name:'person'}) RETURN count(*)",
        )
        == 1
    )
