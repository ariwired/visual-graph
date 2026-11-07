"""Idempotent Neo4j schema: constraints and indexes.

Every statement uses ``IF NOT EXISTS`` so ``apply_schema`` can run any number of times.
"""

from neo4j import Driver

SCHEMA_STATEMENTS: tuple[str, ...] = (
    "CREATE CONSTRAINT image_id_unique IF NOT EXISTS "
    "FOR (n:Image) REQUIRE n.id IS UNIQUE",
    "CREATE CONSTRAINT object_instance_id_unique IF NOT EXISTS "
    "FOR (n:ObjectInstance) REQUIRE n.id IS UNIQUE",
    # Class uniqueness strategy: `name` is the natural key; create classes with MERGE.
    "CREATE CONSTRAINT class_name_unique IF NOT EXISTS "
    "FOR (n:Class) REQUIRE n.name IS UNIQUE",
    # Required properties would need Enterprise edition, so they are enforced in code.
    "CREATE INDEX image_uri IF NOT EXISTS FOR (n:Image) ON (n.uri)",
    "CREATE INDEX object_instance_confidence IF NOT EXISTS "
    "FOR (n:ObjectInstance) ON (n.confidence)",
)

EXPECTED_CONSTRAINTS = frozenset(
    {"image_id_unique", "object_instance_id_unique", "class_name_unique"}
)
EXPECTED_INDEXES = frozenset({"image_uri", "object_instance_confidence"})


def apply_schema(driver: Driver, database: str | None = None) -> None:
    with driver.session(database=database) as session:
        for statement in SCHEMA_STATEMENTS:
            session.run(statement).consume()
        # Wait until indexes are online before returning.
        session.run("CALL db.awaitIndexes(60)").consume()


def existing_schema(driver: Driver, database: str | None = None) -> tuple[set[str], set[str]]:
    """Return ``(constraint names, index names)`` currently in the database."""
    with driver.session(database=database) as session:
        constraints = {r["name"] for r in session.run("SHOW CONSTRAINTS YIELD name")}
        indexes = {r["name"] for r in session.run("SHOW INDEXES YIELD name")}
    return constraints, indexes
