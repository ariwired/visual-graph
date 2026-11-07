from collections.abc import Iterator

import pytest
from neo4j import Driver
from neo4j.exceptions import ConstraintError

from visual_graph.graph.connection import create_driver
from visual_graph.graph.schema import (
    EXPECTED_CONSTRAINTS,
    EXPECTED_INDEXES,
    apply_schema,
    existing_schema,
)

pytestmark = pytest.mark.integration


@pytest.fixture
def driver() -> Iterator[Driver]:
    drv = create_driver()
    with drv.session() as session:
        session.run("MATCH (n) DETACH DELETE n").consume()
    yield drv
    with drv.session() as session:
        session.run("MATCH (n) DETACH DELETE n").consume()
    drv.close()


def test_schema_creates_constraints_and_indexes(driver: Driver) -> None:
    apply_schema(driver)
    constraints, indexes = existing_schema(driver)
    assert EXPECTED_CONSTRAINTS <= constraints
    assert EXPECTED_INDEXES <= indexes


def test_schema_is_idempotent(driver: Driver) -> None:
    apply_schema(driver)
    before = existing_schema(driver)
    apply_schema(driver)
    apply_schema(driver)
    assert existing_schema(driver) == before


@pytest.mark.parametrize(
    ("label", "prop"),
    [("Image", "id"), ("ObjectInstance", "id"), ("Class", "name")],
)
def test_duplicates_are_rejected(driver: Driver, label: str, prop: str) -> None:
    apply_schema(driver)
    with driver.session() as session:
        session.run(f"CREATE (:{label} {{{prop}: 'dup'}})").consume()
        with pytest.raises(ConstraintError):
            session.run(f"CREATE (:{label} {{{prop}: 'dup'}})").consume()


def test_merge_does_not_duplicate_classes(driver: Driver) -> None:
    apply_schema(driver)
    with driver.session() as session:
        for _ in range(3):
            session.run("MERGE (:Class {name: 'person'})").consume()
        count = session.run("MATCH (c:Class {name: 'person'}) RETURN count(c) AS n").single()
    assert count is not None and count["n"] == 1
