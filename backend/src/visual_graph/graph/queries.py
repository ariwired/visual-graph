"""Reusable Cypher queries (``cypher/*.cypher``) for the backend."""

from importlib import resources
from typing import Any

from neo4j import Driver


def load_query(name: str) -> str:
    return (
        resources.files("visual_graph.graph")
        .joinpath(f"cypher/{name}.cypher")
        .read_text(encoding="utf-8")
    )


def run_query(
    driver: Driver, name: str, database: str | None = None, **params: Any
) -> list[dict[str, Any]]:
    """Run the named query file and return rows as dictionaries."""
    with driver.session(database=database) as session:
        return [record.data() for record in session.run(load_query(name), **params)]
