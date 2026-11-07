"""Load the manually created sample scene graph into Neo4j."""

from importlib import resources

from neo4j import Driver

from visual_graph.graph.connection import create_driver, verify_connection
from visual_graph.graph.schema import apply_schema

SAMPLE_IMAGE_ID = "sample-street-1"


def sample_scene_cypher() -> str:
    return (
        resources.files("visual_graph.graph")
        .joinpath("cypher/seed_sample_scene.cypher")
        .read_text(encoding="utf-8")
    )


def seed_sample_scene(driver: Driver, database: str | None = None) -> None:
    """Create the schema (if needed) and the sample scene. Safe to run repeatedly."""
    apply_schema(driver, database)
    with driver.session(database=database) as session:
        session.run(sample_scene_cypher()).consume()


def main() -> None:
    driver = create_driver()
    try:
        verify_connection(driver)
        seed_sample_scene(driver)
    finally:
        driver.close()
    print(f"Sample scene '{SAMPLE_IMAGE_ID}' loaded. Inspect it in Neo4j Browser with:")
    print(f'MATCH p=(:Image {{id: "{SAMPLE_IMAGE_ID}"}})-[*1..2]->() RETURN p')


if __name__ == "__main__":
    main()
